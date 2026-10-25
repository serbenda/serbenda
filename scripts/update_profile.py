#!/usr/bin/env python3
"""Refresh the dynamic parts of the profile README.

- Rewrites the block between <!-- ACTIVITY:START --> and <!-- ACTIVITY:END -->
  with the most recently pushed public repositories.
- Regenerates assets/stats.svg (repos, stars, top languages).

Standard library only. Uses GITHUB_TOKEN when available to avoid rate limits.
"""
from __future__ import annotations

import json
import os
import re
import sys
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from html import escape
from pathlib import Path

USER = os.environ.get("PROFILE_USER", "serbenda")
ROOT = Path(__file__).resolve().parent.parent
READMES = [ROOT / "README.md", ROOT / "README.es.md"]
STATS_SVG = ROOT / "assets" / "stats.svg"
MAX_ITEMS = 5
# Practice / throwaway repos that should not show up on the profile
EXCLUDE = {"testgit", "skills-introduction-to-github"}

LANG_COLORS = {
    "Python": "#3776ab", "JavaScript": "#f7df1e", "TypeScript": "#3178c6",
    "Shell": "#4eaa25", "HTML": "#e34f26", "CSS": "#663399", "Solidity": "#aa6746",
    "HCL": "#7b42bc", "Go": "#00add8", "Dockerfile": "#384d54", "Jinja": "#a52a22",
}

LABELS = {
    "README.md": {"updated": "updated", "today": "today", "days": "{n} days ago", "day": "1 day ago",
                  "months": "{n} months ago", "years": "{n} years ago", "year": "1 year ago",
                  "nodesc": "No description yet."},
    "README.es.md": {"updated": "actualizado", "today": "hoy", "days": "hace {n} días", "day": "hace 1 día",
                     "months": "hace {n} meses", "years": "hace {n} años", "year": "hace 1 año",
                     "nodesc": "Sin descripción todavía."},
}


def fetch_repos(user: str) -> list[dict]:
    repos, page = [], 1
    token = os.environ.get("GITHUB_TOKEN")
    while True:
        url = f"https://api.github.com/users/{user}/repos?per_page=100&type=owner&sort=pushed&page={page}"
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{user}-profile-updater",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        })
        with urllib.request.urlopen(req, timeout=30) as resp:
            batch = json.load(resp)
        repos.extend(batch)
        if len(batch) < 100:
            return repos
        page += 1


def visible(repos: list[dict], user: str) -> list[dict]:
    return [r for r in repos
            if not r.get("fork") and not r.get("private") and not r.get("archived")
            and r["name"].lower() != user.lower()
            and r["name"].lower() not in EXCLUDE]


def ago(iso: str, labels: dict, now: datetime) -> str:
    days = (now - datetime.fromisoformat(iso.replace("Z", "+00:00"))).days
    if days <= 0:
        return labels["today"]
    if days == 1:
        return labels["day"]
    if days < 60:
        return labels["days"].format(n=days)
    if days < 365:
        return labels["months"].format(n=days // 30)
    years = days // 365
    return labels["year"] if years == 1 else labels["years"].format(n=years)


def activity_block(repos: list[dict], labels: dict, now: datetime) -> str:
    rows = []
    for r in repos[:MAX_ITEMS]:
        desc = (r.get("description") or labels["nodesc"]).strip()
        lang = f" · `{r['language']}`" if r.get("language") else ""
        demo = f" · [▶ demo]({r['homepage']})" if r.get("homepage") else ""
        stars = f" · ⭐ {r['stargazers_count']}" if r.get("stargazers_count") else ""
        rows.append(f"- **[{r['name']}]({r['html_url']})**{lang}{stars}{demo} — {desc} "
                    f"<sub>({labels['updated']} {ago(r['pushed_at'], labels, now)})</sub>")
    return "\n".join(rows) if rows else "-"


def replace_block(text: str, block: str) -> str:
    pattern = re.compile(r"(<!-- ACTIVITY:START -->\n).*?(\n<!-- ACTIVITY:END -->)", re.S)
    if not pattern.search(text):
        raise SystemExit("ACTIVITY markers not found")
    return pattern.sub(lambda m: m.group(1) + block + m.group(2), text)


def stats_svg(repos: list[dict]) -> str:
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    langs = Counter(r["language"] for r in repos if r.get("language"))
    top = langs.most_common(5)
    total = sum(n for _, n in top) or 1

    # Stacked language bar
    x, bar = 0.0, []
    for lang, n in top:
        w = 440 * n / total
        bar.append(f'<rect x="{30 + x:.1f}" y="128" width="{w:.1f}" height="10" '
                   f'fill="{LANG_COLORS.get(lang, "#94a3b8")}"/>')
        x += w
    legend = []
    for i, (lang, n) in enumerate(top):
        lx, ly = 30 + (i % 3) * 150, 166 + (i // 3) * 24
        legend.append(
            f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{LANG_COLORS.get(lang, "#94a3b8")}"/>'
            f'<text x="{lx + 16}" y="{ly}" class="t">{escape(lang)} <tspan class="m">{round(100 * n / total)}%</tspan></text>')

    def kpi(xpos: int, value: int, label: str) -> str:
        return (f'<text x="{xpos}" y="78" class="v">{value}</text>'
                f'<text x="{xpos}" y="100" class="m">{label}</text>')

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="500" height="220" viewBox="0 0 500 220" role="img" aria-label="GitHub stats">
<style>
.t{{font:500 13px -apple-system,"Segoe UI",Inter,Helvetica,Arial,sans-serif;fill:#e2e8f0}}
.m{{font:400 12px -apple-system,"Segoe UI",Inter,Helvetica,Arial,sans-serif;fill:#94a3b8}}
.v{{font:800 30px -apple-system,"Segoe UI",Inter,Helvetica,Arial,sans-serif;fill:#f8fafc}}
.h{{font:700 12px ui-monospace,Menlo,Consolas,monospace;fill:#38bdf8;letter-spacing:2px}}
</style>
<rect width="500" height="220" rx="14" fill="#0f1426" stroke="#ffffff" stroke-opacity="0.08"/>
<text x="30" y="36" class="h">PUBLIC WORK · AUTO-UPDATED</text>
{kpi(30, len(repos), "public repos")}{kpi(190, total_stars, "stars")}{kpi(330, len(langs), "languages")}
<rect x="30" y="128" width="440" height="10" rx="5" fill="#1e293b"/>
<clipPath id="bar"><rect x="30" y="128" width="440" height="10" rx="5"/></clipPath>
<g clip-path="url(#bar)">{"".join(bar)}</g>
{"".join(legend)}
</svg>
'''


def main() -> int:
    now = datetime.now(timezone.utc)
    repos = visible(fetch_repos(USER), USER)
    repos.sort(key=lambda r: r["pushed_at"], reverse=True)
    for path in READMES:
        if path.exists():
            text = path.read_text(encoding="utf-8")
            path.write_text(replace_block(text, activity_block(repos, LABELS[path.name], now)), encoding="utf-8")
    STATS_SVG.write_text(stats_svg(repos), encoding="utf-8")
    print(f"Updated with {len(repos)} public repos")
    return 0


if __name__ == "__main__":
    sys.exit(main())
