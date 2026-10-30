"""Shared bits for the 8-bit SVG cards in the README.

Images in a README cannot load web fonts, so each card embeds a small subset of
Press Start 2P (scripts/pixel_font.css: capitals, digits and a few symbols).
Colours are the PICO-8 palette, the same as the website.
"""
from __future__ import annotations

from html import escape
from pathlib import Path

FONT_CSS = (Path(__file__).resolve().parent / "pixel_font.css").read_text(encoding="utf-8").strip()

NAVY, BLACK, PLUM, DKGRAY, GRAY, CREAM = "#1d2b53", "#000000", "#7e2553", "#5f574f", "#c2c3c7", "#fff1e8"
RED, ORANGE, YELLOW, GREEN, BLUE, LILAC, PINK, PEACH = (
    "#ff004d", "#ffa300", "#ffec27", "#00e436", "#29adff", "#83769c", "#ff77a8", "#ffccaa")
SERIES = [BLUE, GREEN, PINK, ORANGE, LILAC, YELLOW]

# Characters present in the embedded font subset
_OK = set(" ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,:;·-–/%&'!?()+#ÁÉÍÓÚÜÑ¿¡▶◀º")


def px(text: str) -> str:
    """Uppercase text restricted to the embedded font, escaped for SVG."""
    up = str(text).upper().replace("→", "-").replace("_", "-")
    return escape("".join(ch if ch in _OK else "-" for ch in up))


def frame(w: int, h: int, color: str = DKGRAY, fill: str = BLACK, b: int = 4) -> str:
    """A filled box with a pixel border and notched corners."""
    return (f'<rect x="{b}" y="0" width="{w - 2 * b}" height="{h}" fill="{fill}"/>'
            f'<rect x="0" y="{b}" width="{w}" height="{h - 2 * b}" fill="{fill}"/>'
            f'<rect x="{b}" y="0" width="{w - 2 * b}" height="{b}" fill="{color}"/>'
            f'<rect x="{b}" y="{h - b}" width="{w - 2 * b}" height="{b}" fill="{color}"/>'
            f'<rect x="0" y="{b}" width="{b}" height="{h - 2 * b}" fill="{color}"/>'
            f'<rect x="{w - b}" y="{b}" width="{b}" height="{h - 2 * b}" fill="{color}"/>')


def svg(w: int, h: int, label: str, body: str) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" '
            f'role="img" aria-label="{escape(label)}" shape-rendering="crispEdges">\n'
            f"<style>{FONT_CSS}\n"
            f".p{{font-family:'PS2P',monospace;font-size:10px}}"
            f".s{{font-family:'PS2P',monospace;font-size:8px}}"
            f".b{{font-family:'PS2P',monospace;font-size:20px}}"
            f".m{{font:400 13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{GRAY}}}</style>\n"
            f"{frame(w, h)}\n{body}\n</svg>\n")
