"""Static SVG figures for the write-up, written by hand so they need no
plotting dependency and regenerate byte-identically on any machine.

Two forms: small multiples of lines (one line per series over ordered x
categories, gaps where a value is missing) and dots with CI whiskers
(series dodged inside each x category, with optional reference lines).
Both paint an opaque light surface so they read on light and dark pages
alike, carry a legend for two or more series, and give every point a
<title> tooltip with its value. Coordinates are printed to one decimal.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from xml.sax.saxutils import escape

WIDTH = 760
PAD = 16
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e1e0d9"
AXIS = "#c3c2b7"
HIGHLIGHT = "#f0efec"
FONT = "system-ui, -apple-system, 'Segoe UI', sans-serif"

# fixed windows as one ordinal blue ramp (darker = bigger chunk), the two
# structure-following chunkings in the first categorical hues after blue
FIXED_RAMP = ("#86b6ef", "#5598e7", "#2a78d6", "#1c5cab", "#104281")
ORANGE = "#eb6834"
AQUA = "#1baf7a"
BLUE = "#2a78d6"


@dataclass(frozen=True)
class Series:
    name: str
    color: str
    values: tuple[float | None, ...]  # one per x category; None leaves a gap


@dataclass(frozen=True)
class Panel:
    title: str
    y_max: float
    y_step: float
    series: tuple[Series, ...]


@dataclass(frozen=True)
class Whiskers:
    name: str
    color: str
    points: tuple[tuple[float, float, float] | None, ...]  # (estimate, low, high) per x category


def _f(x: float) -> str:
    return f"{x:.1f}"


def _text(
    x: float, y: float, s: str, size: int = 11, anchor: str = "start", fill: str = INK_2, bold: bool = False
) -> str:
    weight = ' font-weight="600"' if bold else ""
    return (
        f'<text x="{_f(x)}" y="{_f(y)}" font-size="{size}" text-anchor="{anchor}" fill="{fill}"{weight}>'
        f"{escape(s)}</text>"
    )


def _line(x1: float, y1: float, x2: float, y2: float, color: str, width: float = 1) -> str:
    return f'<line x1="{_f(x1)}" y1="{_f(y1)}" x2="{_f(x2)}" y2="{_f(y2)}" stroke="{color}" stroke-width="{width}"/>'


def _dot(x: float, y: float, color: str, tip: str) -> str:
    return (
        f'<circle cx="{_f(x)}" cy="{_f(y)}" r="4" fill="{color}" stroke="{SURFACE}" stroke-width="2">'
        f"<title>{escape(tip)}</title></circle>"
    )


def _svg(title: str, description: str, height: float, body: Sequence[str]) -> str:
    head = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{_f(height)}" '
        f'viewBox="0 0 {WIDTH} {_f(height)}" role="img" font-family="{FONT}">'
    )
    return "\n".join(
        [
            head,
            f"<title>{escape(title)}</title>",
            f"<desc>{escape(description)}</desc>",
            f'<rect width="{WIDTH}" height="{_f(height)}" fill="{SURFACE}"/>',
            *body,
            "</svg>",
            "",
        ]
    )


def _header(title: str, subtitle: str, legend: Sequence[tuple[str, str]]) -> tuple[list[str], float]:
    """Title, subtitle and a wrapping legend row; returns the elements and the y below them."""
    body = [_text(PAD, 28, title, size=16, fill=INK, bold=True), _text(PAD, 48, subtitle, size=12)]
    x, y = PAD, 72.0
    for name, color in legend if len(legend) > 1 else ():
        width = 30 + 7 * len(name)
        if x + width > WIDTH - PAD:
            x, y = PAD, y + 20
        body.append(_line(x, y - 4, x + 16, y - 4, color, 2))
        body.append(
            f'<circle cx="{_f(x + 8)}" cy="{_f(y - 4)}" r="4" fill="{color}" stroke="{SURFACE}" stroke-width="2"/>'
        )
        body.append(_text(x + 22, y, name, size=12, fill=INK))
        x += width + 12
    return body, y + 16


def _linear(lo: float, hi: float, a: float, b: float) -> Callable[[float], float]:
    """Map [lo, hi] onto [a, b]."""
    return lambda v: a + (b - a) * (v - lo) / (hi - lo)


def _ticks(low: float, high: float, step: float) -> list[float]:
    first = math.ceil(round(low / step, 6))
    last = math.floor(round(high / step, 6))
    return [round(k * step, 6) for k in range(first, last + 1)]


def line_panels(
    title: str,
    subtitle: str,
    description: str,
    x_labels: Sequence[str],
    x_title: str,
    panels: Sequence[Panel],
    columns: int,
) -> str:
    """Small multiples, `columns` panels per row, each with its own y scale
    from 0 to `y_max`; the legend comes from the first panel's series."""
    body, top = _header(title, subtitle, [(s.name, s.color) for s in panels[0].series])
    panel_w = (WIDTH - 2 * PAD) / columns
    plot_h, panel_h = 170.0, 250.0
    for i, panel in enumerate(panels):
        px = PAD + (i % columns) * panel_w
        py = top + (i // columns) * panel_h
        x0, x1 = px + 44, px + panel_w - 16
        y0, y1 = py + 30, py + 30 + plot_h
        body.append(_text(x0, py + 14, panel.title, size=12, fill=INK, bold=True))
        sx = _linear(0, len(x_labels) - 1, x0, x1)
        sy = _linear(0, panel.y_max, y1, y0)

        for tick in _ticks(0, panel.y_max, panel.y_step):
            body.append(_line(x0, sy(tick), x1, sy(tick), AXIS if tick == 0 else GRID))
            body.append(_text(x0 - 6, sy(tick) + 4, f"{tick:.1f}", anchor="end"))
        for k, label in enumerate(x_labels):
            body.append(_text(sx(k), y1 + 16, label, anchor="middle"))
        body.append(_text((x0 + x1) / 2, y1 + 34, x_title, anchor="middle"))
        for series in panel.series:
            path, pen_down = [], False
            for k, v in enumerate(series.values):
                if v is None:
                    pen_down = False
                    continue
                path.append(f"{'L' if pen_down else 'M'}{_f(sx(k))} {_f(sy(v))}")
                pen_down = True
            body.append(
                f'<path d="{" ".join(path)}" fill="none" stroke="{series.color}" stroke-width="2" '
                'stroke-linejoin="round" stroke-linecap="round"/>'
            )
            for k, v in enumerate(series.values):
                if v is not None:
                    body.append(
                        _dot(sx(k), sy(v), series.color, f"{panel.title}, {series.name}, {x_labels[k]}: {v:.4f}")
                    )
    rows = math.ceil(len(panels) / columns)
    return _svg(title, description, top + rows * panel_h, body)


def dot_whiskers(
    title: str,
    subtitle: str,
    description: str,
    x_labels: Sequence[str],
    x_title: str,
    series: Sequence[Whiskers],
    y_step: float,
    references: Sequence[tuple[float, str]] = (),
    highlight: tuple[int, str] | None = None,
) -> str:
    """Each series' estimate as a dot with its CI as a vertical whisker,
    dodged inside each x category; `references` draws labelled horizontal
    lines and `highlight` shades one category with a label above it."""
    body, top = _header(title, subtitle, [(s.name, s.color) for s in series])
    values = [v for s in series for p in s.points if p is not None for v in p] + [0.0]
    values += [value for value, _ in references]
    low = math.floor(round(min(values) / y_step, 6)) * y_step
    high = math.ceil(round(max(values) / y_step, 6)) * y_step
    x0, x1 = PAD + 52, WIDTH - PAD - 8
    y0, y1 = top + 22, top + 22 + 240.0
    band = (x1 - x0) / len(x_labels)
    signed = low < 0
    sy = _linear(low, high, y1, y0)

    if highlight is not None:
        k, label = highlight
        body.append(
            f'<rect x="{_f(x0 + k * band)}" y="{_f(y0 - 16)}" width="{_f(band)}" height="{_f(y1 - y0 + 16)}" fill="{HIGHLIGHT}"/>'
        )
        body.append(_text(x0 + (k + 0.5) * band, y0 - 4, label, anchor="middle"))
    for tick in _ticks(low, high, y_step):
        body.append(_line(x0, sy(tick), x1, sy(tick), AXIS if tick == 0 else GRID))
        body.append(_text(x0 - 6, sy(tick) + 4, f"{tick:+.2f}" if signed and tick else f"{tick:.2f}", anchor="end"))
    for value, label in references:
        if value:
            body.append(_line(x0, sy(value), x1, sy(value), INK_2))
            body.append(_text(x0 + 4, sy(value) - 5, label, fill=INK))
    for k, label in enumerate(x_labels):
        body.append(_text(x0 + (k + 0.5) * band, y1 + 16, label, anchor="middle"))
    body.append(_text((x0 + x1) / 2, y1 + 36, x_title, anchor="middle"))
    for j, s in enumerate(series):
        offset = (j - (len(series) - 1) / 2) * 12
        for k, point in enumerate(s.points):
            if point is None:
                continue
            estimate, lo, hi = point
            x = x0 + (k + 0.5) * band + offset
            body.append(_line(x, sy(lo), x, sy(hi), s.color, 2))
            body.append(
                _dot(x, sy(estimate), s.color, f"{s.name}, {x_labels[k]}: {estimate:+.4f} [{lo:+.4f}, {hi:+.4f}]")
            )
    return _svg(title, description, y1 + 52, body)
