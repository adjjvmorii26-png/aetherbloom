"""Generative SVG renderer for the living lattice."""

from __future__ import annotations
import math
import random
from pathlib import Path
from typing import Dict, Tuple

from core.lattice import Lattice
from core.bloom import BloomState


STATE_COLORS = {
    BloomState.SEED: "#555555",
    BloomState.SPROUTING: "#3d9e6f",
    BloomState.FLOWERING: "#4ecdc4",
    BloomState.MUTATING: "#f7c948",
    BloomState.SYMBIOTIC: "#c77dff",
    BloomState.WILTING: "#e85d5d",
    BloomState.TRANSCENDED: "#6c9eff",
    BloomState.COLLAPSED: "#333333",
}


def _layout(blooms: dict, width: int, height: int) -> Dict[str, Tuple[float, float]]:
    """Simple force-ish circular + jitter layout."""
    n = len(blooms)
    if n == 0:
        return {}
    cx, cy = width / 2, height / 2
    positions = {}
    ids = list(blooms.keys())
    for i, bid in enumerate(ids):
        angle = (2 * math.pi * i) / n + random.uniform(-0.15, 0.15)
        b = blooms[bid]
        r = 80 + min(b.age * 1.8, 140) + b.energy * 30
        r = min(r, min(width, height) * 0.38)
        x = cx + r * math.cos(angle)
        y = cy + r * math.sin(angle)
        positions[bid] = (x, y)
    return positions


def render_svg(lattice: Lattice, path: str | Path, width: int = 900, height: int = 700) -> Path:
    """
    Render the current lattice as a beautiful generative SVG.
    Returns the path written.
    """
    path = Path(path)
    positions = _layout(lattice.blooms, width, height)

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        f'<rect width="100%" height="100%" fill="#0d1117"/>',
        f'<text x="24" y="36" fill="#8b949e" font-family="monospace" font-size="14">'
        f'AetherBloom — {lattice.name} · tick {lattice.tick_count}</text>',
    ]

    # Draw connections first (under nodes)
    drawn = set()
    for bid, bloom in lattice.blooms.items():
        if bid not in positions:
            continue
        x1, y1 = positions[bid]
        for other in bloom.connections:
            if other not in positions:
                continue
            edge = tuple(sorted([bid, other]))
            if edge in drawn:
                continue
            drawn.add(edge)
            x2, y2 = positions[other]
            lines.append(
                f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                f'stroke="#30363d" stroke-width="1.2" stroke-opacity="0.7"/>'
            )

    # Draw blooms
    for bid, bloom in lattice.blooms.items():
        if bid not in positions:
            continue
        x, y = positions[bid]
        color = STATE_COLORS.get(bloom.state, "#888")
        radius = 8 + bloom.energy * 10
        if bloom.state == BloomState.TRANSCENDED:
            radius += 4
            lines.append(
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius+6:.1f}" '
                f'fill="none" stroke="{color}" stroke-width="1.5" stroke-opacity="0.35"/>'
            )
        lines.append(
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{radius:.1f}" '
            f'fill="{color}" fill-opacity="0.85" stroke="#0d1117" stroke-width="1"/>'
        )
        lines.append(
            f'<text x="{x:.1f}" y="{y+radius+14:.1f}" fill="#c9d1d9" '
            f'font-family="monospace" font-size="10" text-anchor="middle">{bid}</text>'
        )
        if bloom.seed and len(lattice.blooms) < 12:
            short = bloom.seed[:22] + ("…" if len(bloom.seed) > 22 else "")
            lines.append(
                f'<text x="{x:.1f}" y="{y+radius+26:.1f}" fill="#6e7681" '
                f'font-family="monospace" font-size="9" text-anchor="middle">{_escape(short)}</text>'
            )

    legend_y = height - 28
    lines.append(
        f'<text x="24" y="{legend_y}" fill="#6e7681" font-family="monospace" font-size="11">'
        f'alive {lattice.alive_count()} · pollen {len(lattice.pollen.grains)} · '
        f'entropy {lattice.entropy.global_entropy:.2f}</text>'
    )

    lines.append("</svg>")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )
