#!/usr/bin/env python3
"""Minimal example: plant three seeds and run 30 ticks."""

import sys
sys.path.insert(0, "..")

from core.lattice import Lattice

garden = Lattice(name="example plot")

garden.plant("the color of time when no one is looking")
garden.plant("a library that only appears in dreams")
garden.plant("what machines dream of when they power down")

print("Starting 30-tick simulation...\n")

for i in range(30):
    events = garden.tick()
    if events:
        print(f"── tick {i+1} ──")
        for e in events:
            print(f"  {e}")
        print()

print(garden.status())
print("\nDone. Some blooms may have transcended or collapsed.")
