#!/usr/bin/env python3
"""Collect visit stats for every public repo and its GitHub Pages site.

Two sources:

1. GitHub traffic API (views and clones of github.com/<user>/<repo>).
   GitHub only keeps the last 14 days, so every run merges them into
   docs/data/traffic.json and the history keeps growing day by day.
   Needs a personal access token in TRAFFIC_TOKEN: the default
   GITHUB_TOKEN of a workflow cannot read other repos' traffic.

2. GoatCounter (visits to <user>.github.io/<repo>/). GitHub Pages has no
   analytics of its own, so each site loads the GoatCounter script and this
   collector reads the public counters (no token needed). Games also send a
   "partida/<repo>" event when a match starts, stored as "plays". The site code is
   taken from the GOATCOUNTER_CODE variable (default: the GitHub user).

Outputs:
- docs/data/traffic.json   history used by the dashboard web page
- assets/traffic.svg       card for README.md
- assets/traffic.es.svg    card for README.es.md

Standard library only.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from html import escape
from pathlib import Path

from update_profile import EXCLUDE, USER

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "docs" / "data" / "traffic.json"
CARDS = {
    "en": ROOT / "assets" / "traffic.svg",
    "es": ROOT / "assets" / "traffic.es.svg",
}
GOAT = (os.environ.get("GOATCOUNTER_CODE") or USER).strip()
MAX_REFERRERS = 10


# ---------------------------------------------------------------- HTTP helpers

def get_json(url: str, token: str | None = None):
    """GET a JSON document. HTTP errors carry the URL so failures say what was asked."""
    headers = {"Accept": "application/vnd.github+json", "User-Agent": f"{USER}-traffic"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as err:
        err.msg = f"{err.msg} for {url.split('?')[0]}"
        raise


def gh(path: str, token: str | None):
    return get_json(f"https://api.github.com{path}", token)


def list_repos(token: str | None) -> list[dict]:
    """Public, non-fork, non-archived repos owned by USER."""
    repos, page = [], 1
    while True:
        batch = gh(f"/users/{USER}/repos?type=owner&per_page=100&page={page}", token)
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return [r for r in repos
            if r["owner"]["login"].lower() == USER.lower()
            and not r.get("fork") and not r.get("private") and not r.get("archived")
            and r["name"].lower() not in EXCLUDE]


def pages_path(name: str) -> str:
    return "/" if name.lower() == f"{USER}.github.io".lower() else f"/{name}/"


def goat_count(path: str) -> int | None:
    """Total visits GoatCounter has for a path, or None if unknown."""
    if not GOAT:
        return None
    url = f"https://{GOAT}.goatcounter.com/counter/{urllib.parse.quote(path, safe='')}.json"
    try:
        data = get_json(url)
    except urllib.error.HTTPError as err:
        return 0 if err.code == 404 else None   # 404 = no visits yet
    except Exception:   # site not created yet, network hiccup, unexpected answer
        return None
    digits = "".join(ch for ch in str(data.get("count", "")) if ch.isdigit())
    return int(digits) if digits else 0


# ------------------------------------------------------------------- merging

def load() -> dict:
    if DATA.exists():
        return json.loads(DATA.read_text(encoding="utf-8"))
    return {"repos": {}, "site": {}}


def merge_days(store: dict, items: list[dict]) -> None:
    """GitHub returns one entry per day; the latest answer for a day wins."""
    for it in items:
        day = it["timestamp"][:10]
        store[day] = [it["count"], it["uniques"]]


def collect(data: dict, now: datetime) -> dict:
    token = os.environ.get("TRAFFIC_TOKEN") or None          # only for the traffic endpoints
    list_token = os.environ.get("GITHUB_TOKEN") or None      # public repo list
    today = now.strftime("%Y-%m-%d")

    if not token:
        print("TRAFFIC_TOKEN not set: skipping repo views/clones, only Pages counters.")

    for r in list_repos(list_token):
        name = r["name"]
        entry = data["repos"].setdefault(name, {"views": {}, "clones": {}, "pages_hits": {}})
        entry.update({
            "url": r["html_url"],
            "description": r.get("description") or "",
            "language": r.get("language"),
            "stars": r.get("stargazers_count", 0),
            "pushed_at": r.get("pushed_at"),
            "pages": bool(r.get("has_pages")),
        })
        if entry["pages"]:
            entry["pages_url"] = f"https://{USER}.github.io{pages_path(name)}"
            entry["pages_path"] = pages_path(name)

        if token:
            base = f"/repos/{USER}/{name}/traffic"
            try:
                merge_days(entry["views"], gh(f"{base}/views", token).get("views", []))
                merge_days(entry["clones"], gh(f"{base}/clones", token).get("clones", []))
                entry["referrers"] = gh(f"{base}/popular/referrers", token)[:MAX_REFERRERS]
            except urllib.error.HTTPError as err:
                print(f"::warning title=collect_traffic::{name}: the traffic API answered {err.code}. "
                      "The TRAFFIC_TOKEN needs read access to Administration on this repo.")

        if entry["pages"]:
            hits = goat_count(entry["pages_path"])
            if hits is not None:
                entry["pages_hits"][today] = hits
            # Games send a "partida/<repo>" event each time a match starts
            plays = goat_count(f"partida/{name}")
            if plays:
                entry.setdefault("plays", {})[today] = plays

    total = goat_count("TOTAL")
    if total is not None:
        data["site"][today] = total

    data.update({"user": USER, "goatcounter": GOAT, "updated": now.isoformat(timespec="seconds")})
    return data


# --------------------------------------------------------------------- totals

def last(series: dict) -> int:
    return series[max(series)] if series else 0


def totals(entry: dict) -> tuple[int, int]:
    views = sum(v[0] for v in entry.get("views", {}).values())
    return views, last(entry.get("pages_hits", {}))


# ----------------------------------------------------------------------- card

TEXT = {
    "en": {"head": "Visits", "repo": "views on GitHub", "pages": "game visits", "since": "since",
           "none": "No data yet"},
    "es": {"head": "Visitas", "repo": "vistas en GitHub", "pages": "visitas a los juegos", "since": "desde",
           "none": "Todavía no hay datos"},
}
PROJECTS = ROOT / "docs" / "data" / "projects.json"


def titles() -> dict:
    """Display names from the website's project list, so the card matches it."""
    try:
        p = json.loads(PROJECTS.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return {x["repo"]: x["title"] for x in p.get("games", []) + p.get("tools", [])}


def card(data: dict, lang: str) -> str:
    """Visits card: GitHub views and Pages visits, top five projects."""
    import pixel as P
    t, names = TEXT[lang], titles()
    rows = []
    for name, e in data["repos"].items():
        v, p = totals(e)
        if v + p:
            rows.append((names.get(name, name), v, p))
    rows.sort(key=lambda r: r[1] + r[2], reverse=True)
    repo_total = sum(r[1] for r in rows)
    pages_total = sum(r[2] for r in rows)
    days = sorted(d for e in data["repos"].values() for d in e.get("views", {}))

    body = [f'<rect x="28" y="30" width="8" height="8" fill="{P.YELLOW}"/>'
            f'<text x="44" y="39" class="p" fill="{P.CREAM}">{P.px(t["head"])}</text>']
    if days:
        body.append(f'<text x="472" y="40" class="s" fill="{P.GRAY}" text-anchor="end">'
                    f'{t["since"]} {days[0][8:10]}/{days[0][5:7]}/{days[0][:4]}</text>')
    body.append(f'<text x="28" y="88" class="b" fill="{P.BLUE}">{repo_total:,}</text>'
                f'<text x="28" y="110" class="s" fill="{P.GRAY}">{t["repo"]}</text>'
                f'<text x="260" y="88" class="b" fill="{P.GREEN}">{pages_total:,}</text>'
                f'<text x="260" y="110" class="s" fill="{P.GRAY}">{t["pages"]}</text>')
    peak = max((r[1] + r[2] for r in rows), default=1) or 1
    for i, (name, v, p) in enumerate(rows[:5]):
        y = 140 + i * 24
        wv = round(132 * v / peak / 4) * 4
        wp = round(132 * p / peak / 4) * 4
        label = name if len(name) <= 26 else name[:25] + "…"
        body.append(
            f'<text x="28" y="{y + 9}" class="s" fill="{P.YELLOW}">{i + 1}</text>'
            f'<text x="50" y="{y + 9}" class="s" fill="{P.CREAM}">{P.px(label)}</text>'
            f'<rect x="268" y="{y}" width="132" height="10" fill="#141e3d"/>'
            f'<rect x="268" y="{y}" width="{wv}" height="10" fill="{P.BLUE}"/>'
            f'<rect x="{268 + wv}" y="{y}" width="{wp}" height="10" fill="{P.GREEN}"/>'
            f'<text x="472" y="{y + 9}" class="s" fill="{P.CREAM}" text-anchor="end">{v + p}</text>')
    if not rows:
        body.append(f'<text x="28" y="170" class="s" fill="{P.PINK}">{P.px(t["none"])}</text>')
    return P.svg(500, 268, t["head"], "".join(body))


def main() -> int:
    try:
        return run()
    except Exception as err:
        # Shown as an annotation on the workflow run, so the cause is visible without opening logs
        import traceback
        where = traceback.extract_tb(err.__traceback__)[-1]
        print(f"::error title=collect_traffic::{type(err).__name__}: {err} "
              f"(line {where.lineno}, {where.name})")
        raise


def run() -> int:
    now = datetime.now(timezone.utc)
    data = collect(load(), now)
    DATA.parent.mkdir(parents=True, exist_ok=True)
    DATA.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    for lang, path in CARDS.items():
        path.write_text(card(data, lang), encoding="utf-8")
    print(f"Traffic stored for {len(data['repos'])} repos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
