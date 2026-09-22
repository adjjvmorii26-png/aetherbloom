#!/usr/bin/env python3
"""
AetherBloom Garden — main entry point.

Plant seeds. Watch the lattice breathe.
Save it. Render it. Come back later.
"""

from __future__ import annotations
import argparse
import time
from pathlib import Path

from core.lattice import Lattice
from core.bloom import BloomState
from core.persistence import save_garden, load_garden


class C:
    RESET = "\033[0m"
    DIM = "\033[2m"
    GREEN = "\033[32m"
    CYAN = "\033[36m"
    YELLOW = "\033[33m"
    MAGENTA = "\033[35m"
    RED = "\033[31m"
    BOLD = "\033[1m"
    BLUE = "\033[34m"


STATE_COLOR = {
    BloomState.SEED: C.DIM,
    BloomState.SPROUTING: C.GREEN,
    BloomState.FLOWERING: C.CYAN,
    BloomState.MUTATING: C.YELLOW,
    BloomState.SYMBIOTIC: C.MAGENTA,
    BloomState.WILTING: C.RED,
    BloomState.TRANSCENDED: C.BOLD + C.BLUE,
    BloomState.COLLAPSED: C.DIM,
}


def clear():
    print("\033[H\033[J", end="")


def render(lattice: Lattice, events: list[str]):
    clear()
    print(f"{C.BOLD}{C.CYAN}🌱 AetherBloom{C.RESET}  —  {lattice.name}")
    print(f"{C.DIM}tick {lattice.tick_count} · alive {lattice.alive_count()} · pollen {len(lattice.pollen.grains)}{C.RESET}")
    print("─" * 64)

    for b in sorted(lattice.blooms.values(), key=lambda x: (-x.age, x.id)):
        color = STATE_COLOR.get(b.state, C.RESET)
        energy_bar = "█" * int(b.energy * 8) + "░" * (8 - int(b.energy * 8))
        print(f"  {color}{b.id}{C.RESET}  {b.state.name:<11}  E[{energy_bar}]  {C.DIM}{b.seed[:42]}{C.RESET}")
        if b.connections:
            print(f"       {C.DIM}↔ {', '.join(b.connections)}{C.RESET}")
        if b.state == BloomState.TRANSCENDED and b.archetype:
            print(f"       {C.BLUE}✦ {b.archetype[:50]}{C.RESET}")

    if events:
        print()
        print(f"{C.YELLOW}events this tick:{C.RESET}")
        for e in events[-6:]:
            print(f"  · {e}")

    print()
    print(f"{C.DIM}ctrl-c to stop & auto-save · garden remembers{C.RESET}")


def run_garden(
    seeds: list[str],
    ticks: int = 0,
    delay: float = 1.1,
    name: str = "midnight garden",
    load_path: str | None = None,
    save_path: str | None = None,
    svg_every: int = 0,
):
    if load_path and Path(load_path).exists():
        lattice = load_garden(load_path)
        print(f"{C.GREEN}Restored garden from {load_path}{C.RESET}")
        time.sleep(0.8)
    else:
        lattice = Lattice(name=name)
        if not seeds:
            seeds = [
                "what if silence had a temperature?",
                "the geometry of almost-touching",
                "a clock that runs on forgotten names",
            ]
        for s in seeds:
            lattice.plant(s)
        print(f"{C.GREEN}Garden planted with {len(seeds)} seed(s). Beginning life...{C.RESET}")
        time.sleep(1.0)

    save_path = save_path or "garden_state.json"
    svg_path = Path("garden_lattice.svg")

    try:
        tick = 0
        while True:
            events = lattice.tick()
            render(lattice, events)
            tick += 1

            if svg_every and tick % svg_every == 0:
                from viz.svg_lattice import render_svg
                render_svg(lattice, svg_path)

            if ticks and tick >= ticks:
                break
            time.sleep(delay)
    except KeyboardInterrupt:
        print(f"\n{C.CYAN}Garden paused.{C.RESET}")
    finally:
        p = save_garden(lattice, save_path)
        print(f"{C.GREEN}Saved → {p}{C.RESET}")
        from viz.svg_lattice import render_svg
        render_svg(lattice, svg_path)
        print(f"{C.GREEN}SVG lattice → {svg_path}{C.RESET}")
        print()
        print(lattice.status())


def main():
    parser = argparse.ArgumentParser(
        description="AetherBloom — plant seeds, watch autonomous thought-blooms evolve"
    )
    parser.add_argument("--seed", "-s", action="append", default=[], help="Plant seed(s)")
    parser.add_argument("--ticks", "-t", type=int, default=0, help="Run N ticks then stop (0=forever)")
    parser.add_argument("--delay", "-d", type=float, default=1.1, help="Seconds between ticks")
    parser.add_argument("--name", "-n", default="midnight garden", help="Garden name")
    parser.add_argument("--load", "-l", default=None, help="Load garden from JSON")
    parser.add_argument("--save", default="garden_state.json", help="Save path")
    parser.add_argument("--svg-every", type=int, default=0, help="Write SVG every N ticks")
    args = parser.parse_args()

    run_garden(
        seeds=args.seed,
        ticks=args.ticks,
        delay=args.delay,
        name=args.name,
        load_path=args.load,
        save_path=args.save,
        svg_every=args.svg_every,
    )


if __name__ == "__main__":
    main()
