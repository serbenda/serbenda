#!/usr/bin/env python3
"""Collect visit stats for every public repo and its GitHub Pages site.

Two sources:

1. GitHub traffic API (views and clones of github.com/<user>/<repo>).
   GitHub only keeps the last 14 days, so every run merges them into
   data/traffic.json and the history keeps growing day by day.
   Needs a personal access token in TRAFFIC_TOKEN: the default
   GITHUB_TOKEN of a workflow cannot read other repos' traffic.

2. GoatCounter (visits to <user>.github.io/<repo>/). GitHub Pages has no
   analytics of its own, so each site loads the GoatCounter script and this
   collector reads the public counters (no token needed). Games also send a
   "partida/<repo>" event when a match starts, stored as "plays". The site code is
   taken from the GOATCOUNTER_CODE variable (default: the GitHub user). With a read-only
   API key in the GOATCOUNTER_TOKEN secret it also stores phone vs computer, countries and
   referrers for the last 30 days, for the whole site and each project.

Outputs:
- data/traffic.json        history read by the website (bendi.dev, repo serbenda.github.io)
- assets/traffic.svg       card for README.md
- assets/traffic.es.svg    card for README.es.md

Standard library only.
"""
from __future__ import annotations

import json
import re
import time
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from html import escape
from pathlib import Path

from update_profile import EXCLUDE, USER

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "traffic.json"
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


def site_pages(name: str, branch: str) -> list[str]:
    """Every page of a project's site, from the sitemap.xml in its repo (full URLs).

    Multi-page sites (bolsillo, hucha…) count each page separately in GoatCounter, so the
    project's visits are the sum of all of them. Single-page games have no sitemap: [].
    """
    url = f"https://raw.githubusercontent.com/{USER}/{name}/{branch}/sitemap.xml"
    req = urllib.request.Request(url, headers={"User-Agent": f"{USER}-traffic"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            xml = resp.read().decode("utf-8", "replace")
    except Exception:   # no sitemap, or GitHub hiccup: fall back to the home page
        return []
    return re.findall(r"<loc>\s*([^<\s]+)\s*</loc>", xml)


def goat_path(name: str, url: str) -> str:
    """The path a page of `name` is counted under in GoatCounter.

    Sites on their own subdomain (bolsillo.bendi.dev) prefix their paths with /<name>,
    so they don't mix with bendi.dev; pages under bendi.dev/<name>/ already have it.
    """
    path = urllib.parse.urlparse(url).path or "/"
    return path if path.startswith(f"/{name}/") or path == f"/{name}" else f"/{name}{path}"


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


# ----------------------------------------------------- GoatCounter API (optional)
# With a read-only API key in GOATCOUNTER_TOKEN, the collector also stores, for the last
# GC_DAYS days: phone vs computer, countries and where visitors come from, for the whole
# site and for each project. Without the key this part is skipped.
GC_DAYS = 30
PHONE_SIZES = {"phones", "tablets and large phones"}


def gc_api(page: str, token: str, start: str, end: str, paths: list[str] | None = None, limit: int = 10) -> list[dict]:
    """[{name, count}] for a GoatCounter stats page (sizes, locations, toprefs…), or [] on error."""
    query = {"start": start, "end": end, "limit": str(limit)}
    if paths:
        query.update(path_by_name="true", include_paths=",".join(paths))
    url = f"https://{GOAT}.goatcounter.com/api/v0/stats/{page}?{urllib.parse.urlencode(query)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}",
                                               "Content-Type": "application/json",
                                               "User-Agent": f"{USER}-traffic"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            stats = json.load(resp).get("stats") or []
    except Exception as err:
        print(f"::warning title=collect_traffic::GoatCounter API {page}: {err}")
        return []
    finally:
        time.sleep(0.4)   # well under the API rate limit
    return [{"name": x.get("name") or "(unknown)", "count": int(x.get("count") or 0)} for x in stats if x.get("count")]


def devices(sizes: list[dict]) -> dict:
    """Screen sizes grouped into phone (and tablet) vs computer."""
    out = {"phone": 0, "computer": 0}
    for x in sizes:
        name = x["name"].lower()
        if name in PHONE_SIZES:
            out["phone"] += x["count"]
        elif "computer" in name:
            out["computer"] += x["count"]
    return out


def collect_gc(data: dict, now: datetime) -> None:
    token = os.environ.get("GOATCOUNTER_TOKEN") or None
    if not token:
        print("GOATCOUNTER_TOKEN not set: skipping devices, countries and referrers.")
        return
    end = now.replace(minute=0, second=0, microsecond=0)
    start = end - timedelta(days=GC_DAYS)
    span = [start.strftime("%Y-%m-%dT%H:%M:%SZ"), end.strftime("%Y-%m-%dT%H:%M:%SZ")]
    site = {
        "days": GC_DAYS, "start": span[0][:10], "end": span[1][:10],
        "devices": devices(gc_api("sizes", token, *span)),
        "countries": gc_api("locations", token, *span, limit=12),
        "referrers": gc_api("toprefs", token, *span, limit=12),
    }
    if not any(site["devices"].values()) and not site["countries"]:
        print("::warning title=collect_traffic::The GoatCounter API returned nothing: check GOATCOUNTER_TOKEN.")
        return
    data["gc"] = site
    for name, entry in data["repos"].items():
        if not entry.get("pages"):
            continue
        # GoatCounter stores paths without the trailing slash
        names = [p.rstrip("/") or "/" for p in entry.get("pages_paths") or [entry.get("pages_path", f"/{name}/")]]
        entry["gc"] = {
            "devices": devices(gc_api("sizes", token, *span, paths=names)),
            "referrers": gc_api("toprefs", token, *span, paths=names, limit=5),
        }


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
            # The user site's sitemap is bendi.dev itself: only its home page belongs to it
            urls = [] if pages_path(name) == "/" else site_pages(name, r.get("default_branch") or "main")
            if urls:
                entry["pages_url"] = urls[0]
            entry["pages_paths"] = sorted({goat_path(name, u) for u in urls}) or [entry["pages_path"]]

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
            counts = [goat_count(p) for p in entry["pages_paths"]]
            known = [c for c in counts if c is not None]
            if known:
                entry["pages_hits"][today] = sum(known)
            # Games send a "partida/<repo>" event each time a match starts
            plays = goat_count(f"partida/{name}")
            if plays:
                entry.setdefault("plays", {})[today] = plays

    collect_gc(data, now)

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
PROJECTS_URL = f"https://raw.githubusercontent.com/{USER}/{USER}.github.io/main/data/projects.json"


def projects() -> dict:
    """The website's project list (repo serbenda.github.io), or empty if unreachable."""
    try:
        return get_json(PROJECTS_URL)
    except Exception:
        return {}


def titles() -> dict:
    """Display names from the website's project list, so the card matches it."""
    p = projects()
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
