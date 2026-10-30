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
    """8-bit card: public repos, stars, languages and a stepped language bar."""
    import pixel as P
    total_stars = sum(r.get("stargazers_count", 0) for r in repos)
    langs = Counter(r["language"] for r in repos if r.get("language"))
    top = langs.most_common(5)
    total = sum(n for _, n in top) or 1

    def kpi(x: int, value: int, label: str, color: str) -> str:
        return (f'<text x="{x}" y="88" class="b" fill="{color}">{value}</text>'
                f'<text x="{x}" y="110" class="s" fill="{P.GRAY}">{P.px(label)}</text>')

    # Language bar in 4px steps, each language with its own palette colour
    x, bar, legend = 28.0, [], []
    for i, (lang, n) in enumerate(top):
        w = round(444 * n / total / 4) * 4 if i < len(top) - 1 else 472 - x
        bar.append(f'<rect x="{x:.0f}" y="132" width="{max(w, 4):.0f}" height="12" fill="{P.SERIES[i % 6]}"/>')
        x += w
        lx, ly = 28 + (i % 3) * 152, 172 + (i // 3) * 22
        legend.append(f'<rect x="{lx}" y="{ly - 9}" width="8" height="8" fill="{P.SERIES[i % 6]}"/>'
                      f'<text x="{lx + 14}" y="{ly}" class="s" fill="{P.CREAM}">{P.px(lang)} '
                      f'{round(100 * n / total)}%</text>')

    body = (f'<rect x="28" y="30" width="8" height="8" fill="{P.YELLOW}"/>'
            f'<text x="44" y="39" class="p" fill="{P.CREAM}">GitHub</text>'
            + kpi(28, len(repos), "public repos", P.BLUE) + kpi(188, total_stars, "stars", P.YELLOW)
            + kpi(340, len(langs), "languages", P.GREEN)
            + f'<rect x="28" y="132" width="444" height="12" fill="#141e3d"/>' + "".join(bar) + "".join(legend))
    return P.svg(500, 220, "GitHub stats", body)


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
