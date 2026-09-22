#!/usr/bin/env python3
"""
AetherBloom Garden — main entry point.

Plant seeds. Watch the lattice breathe.
"""

from __future__ import annotations
import argparse
import time
import sys
import random

from core.lattice import Lattice
from core.bloom import BloomState


# ANSI colors for terminal life
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
    print(f"{C.DIM}ctrl-c to stop · garden continues even when you look away{C.RESET}")


def run_garden(seeds: list[str], ticks: int = 0, delay: float = 1.1, name: str = "midnight garden"):
    lattice = Lattice(name=name)

    # plant initial seeds
    if not seeds:
        seeds = [
            "what if silence had a temperature?",
            "the geometry of almost-touching",
            "a clock that runs on forgotten names",
        ]
    for s in seeds:
        lattice.plant(s)

    print(f"{C.GREEN}Garden planted with {len(seeds)} seed(s). Beginning life...{C.RESET}")
    time.sleep(1.2)

    try:
        tick = 0
        while True:
            events = lattice.tick()
            render(lattice, events)
            tick += 1
            if ticks and tick >= ticks:
                break
            time.sleep(delay)
    except KeyboardInterrupt:
        print(f"\n{C.CYAN}Garden paused. State lives in memory until process ends.{C.RESET}")
        print(lattice.status())


def main():
    parser = argparse.ArgumentParser(
        description="AetherBloom — plant seeds, watch autonomous thought-blooms evolve"
    )
    parser.add_argument(
        "--seed", "-s", action="append", default=[],
        help="Plant one or more seeds (can be repeated)"
    )
    parser.add_argument(
        "--ticks", "-t", type=int, default=0,
        help="Run for N ticks then stop (0 = forever)"
    )
    parser.add_argument(
        "--delay", "-d", type=float, default=1.1,
        help="Seconds between ticks"
    )
    parser.add_argument(
        "--name", "-n", default="midnight garden",
        help="Name of this garden instance"
    )
    args = parser.parse_args()

    run_garden(
        seeds=args.seed,
        ticks=args.ticks,
        delay=args.delay,
        name=args.name,
    )


if __name__ == "__main__":
    main()
