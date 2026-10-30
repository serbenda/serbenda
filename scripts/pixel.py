"""Shared bits for the SVG cards in the README: same palette as the website,
system monospace text (images in a README cannot load web fonts) and a square
frame with notched corners."""
from __future__ import annotations

from html import escape


NAVY, BLACK, PLUM, DKGRAY, GRAY, CREAM = "#1d2b53", "#000000", "#7e2553", "#5f574f", "#c2c3c7", "#fff1e8"
RED, ORANGE, YELLOW, GREEN, BLUE, LILAC, PINK, PEACH = (
    "#ff004d", "#ffa300", "#ffec27", "#00e436", "#29adff", "#83769c", "#ff77a8", "#ffccaa")
SERIES = [BLUE, GREEN, PINK, ORANGE, LILAC, YELLOW]


def px(text: str) -> str:
    """Text escaped for SVG."""
    return escape(str(text).replace("→", "->"))


def frame(w: int, h: int, color: str = "#2c3a6b", fill: str = "#18224a", b: int = 2) -> str:
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
            f"<style>.p{{font:700 14px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}"
            f".s{{font:500 12px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}"
            f".b{{font:700 28px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}}"
            f".m{{font:400 13px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{GRAY}}}</style>\n"
            f"{frame(w, h)}\n{body}\n</svg>\n")
