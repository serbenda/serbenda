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
    headers = {"Accept": "application/vnd.github+json", "User-Agent": f"{USER}-traffic"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def gh(path: str, token: str | None):
    return get_json(f"https://api.github.com{path}", token)


def list_repos(token: str | None) -> list[dict]:
    """Public, non-fork, non-archived repos owned by USER."""
    repos, page = [], 1
    while True:
        if token:
            path = f"/user/repos?affiliation=owner&visibility=public&per_page=100&page={page}"
        else:
            path = f"/users/{USER}/repos?type=owner&per_page=100&page={page}"
        batch = gh(path, token)
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
    except (urllib.error.URLError, TimeoutError, ValueError):
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
    token = os.environ.get("TRAFFIC_TOKEN") or None
    list_token = token or os.environ.get("GITHUB_TOKEN") or None
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
                print(f"  {name}: traffic API answered {err.code}, check the token permissions")

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
    "en": {"head": "VISITS · AUTO-UPDATED", "repo": "repo views", "pages": "Pages visits",
           "top": "Most visited", "since": "since", "none": "Collecting the first data…"},
    "es": {"head": "VISITAS · SE ACTUALIZA SOLO", "repo": "vistas a repos", "pages": "visitas a Pages",
           "top": "Lo más visto", "since": "desde", "none": "Recogiendo los primeros datos…"},
}


def fmt(n: int, lang: str) -> str:
    return f"{n:,}".replace(",", "." if lang == "es" else ",")


def card(data: dict, lang: str) -> str:
    t = TEXT[lang]
    rows = []
    for name, e in data["repos"].items():
        v, p = totals(e)
        if v + p:
            rows.append((name, v, p))
    rows.sort(key=lambda r: r[1] + r[2], reverse=True)
    repo_total = sum(r[1] for r in rows)
    pages_total = sum(r[2] for r in rows)
    days = sorted(d for e in data["repos"].values() for d in e.get("views", {}))
    since = f'{t["since"]} {days[0]}' if days else ""

    bars = []
    peak = max((r[1] + r[2] for r in rows), default=1) or 1
    for i, (name, v, p) in enumerate(rows[:4]):
        y = 150 + i * 26
        wv, wp = 180 * v / peak, 180 * p / peak
        label = escape(name if len(name) <= 22 else name[:21] + "…")
        bars.append(
            f'<text x="30" y="{y + 9}" class="t">{label}</text>'
            f'<clipPath id="b{i}"><rect x="226" y="{y}" width="180" height="10" rx="5"/></clipPath>'
            f'<rect x="226" y="{y}" width="180" height="10" rx="5" fill="#1e293b"/>'
            f'<g clip-path="url(#b{i})">'
            f'<rect x="226" y="{y}" width="{wv:.1f}" height="10" fill="#38bdf8"/>'
            f'<rect x="{226 + wv:.1f}" y="{y}" width="{wp:.1f}" height="10" fill="#36d399"/></g>'
            f'<text x="470" y="{y + 9}" class="t" text-anchor="end">{fmt(v + p, lang)}</text>')
    if not bars:
        bars.append(f'<text x="30" y="160" class="m">{t["none"]}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="260" viewBox="0 0 500 260" role="img" aria-label="{escape(t["head"])}">
<style>
.t{{font:500 13px -apple-system,"Segoe UI",Inter,Helvetica,Arial,sans-serif;fill:#e2e8f0}}
.m{{font:400 12px -apple-system,"Segoe UI",Inter,Helvetica,Arial,sans-serif;fill:#94a3b8}}
.v{{font:800 30px -apple-system,"Segoe UI",Inter,Helvetica,Arial,sans-serif;fill:#f8fafc}}
.h{{font:700 12px ui-monospace,Menlo,Consolas,monospace;fill:#38bdf8;letter-spacing:2px}}
</style>
<rect width="500" height="260" rx="14" fill="#0f1426" stroke="#ffffff" stroke-opacity="0.08"/>
<text x="30" y="36" class="h">{escape(t["head"])}</text>
<text x="470" y="36" class="m" text-anchor="end">{escape(since)}</text>
<rect x="30" y="58" width="4" height="40" rx="2" fill="#38bdf8"/>
<text x="44" y="82" class="v">{fmt(repo_total, lang)}</text><text x="44" y="102" class="m">{t["repo"]}</text>
<rect x="260" y="58" width="4" height="40" rx="2" fill="#36d399"/>
<text x="274" y="82" class="v">{fmt(pages_total, lang)}</text><text x="274" y="102" class="m">{t["pages"]}</text>
<text x="30" y="134" class="h">{escape(t["top"].upper())}</text>
{"".join(bars)}
</svg>
'''


def main() -> int:
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
