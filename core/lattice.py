"""The Lattice — the living garden graph and its physics."""

from __future__ import annotations
from typing import Dict, List, Optional, Tuple
import random
import time

from .bloom import Bloom, BloomState
from .entropy import EntropyField
from .pollen import PollenTrail


class Lattice:
    """
    The garden itself.
    Holds blooms, manages connections, entropy, and pollen.
    """

    def __init__(self, name: str = "unnamed garden"):
        self.name = name
        self.blooms: Dict[str, Bloom] = {}
        self.entropy = EntropyField()
        self.pollen = PollenTrail()
        self.tick_count = 0
        self.history: List[str] = []
        self.created_at = time.time()

    def plant(self, seed: str) -> Bloom:
        """Plant a new seed. Returns the newborn bloom."""
        bloom = Bloom(seed=seed.strip())
        self.blooms[bloom.id] = bloom
        self.entropy.register(bloom.id)
        msg = f"planted [{bloom.id}] «{seed[:50]}»"
        self.history.append(msg)
        return bloom

    def tick(self) -> List[str]:
        """
        Advance the entire garden by one step.
        Returns a list of event strings that happened this tick.
        """
        self.tick_count += 1
        events: List[str] = []

        active_ids = list(self.blooms.keys())
        for bid in active_ids:
            bloom = self.blooms[bid]
            if bloom.state in (BloomState.COLLAPSED, BloomState.TRANSCENDED):
                continue

            nearby = [g.content for g in self.pollen.nearby(bid, limit=3)]
            e = self.entropy.tick(bid, activity=0.1 if nearby else 0.05)

            insight = bloom.grow(pollen_nearby=nearby, entropy=e)
            if insight:
                events.append(f"{bloom.id}: {insight}")
                if random.random() < 0.45:
                    self.pollen.release(insight, origin=bid)

            if bloom.try_transcend():
                events.append(f"✦ {bloom.id} transcended → archetype: {bloom.archetype}")
                self.pollen.release(f"ARCHETYPE: {bloom.archetype}", origin=bid, tags=["transcendent"])

            if self.entropy.should_mutate(bid) and bloom.state == BloomState.FLOWERING:
                insight = bloom._mutate(entropy=e)
                events.append(f"{bloom.id}: {insight}")
                self.entropy.inject_novelty(bid, 0.4)

            if self.entropy.should_collapse(bid):
                bloom.state = BloomState.COLLAPSED
                events.append(f"{bloom.id}: collapsed under entropy overload")

        self.pollen.tick()

        if len(self.blooms) >= 2 and random.random() < 0.25:
            events.extend(self._try_connect())

        if self.tick_count > 15 and random.random() < 0.06:
            theme = self.pollen.strongest_theme()
            if theme:
                child = self.plant(f"echo of: {theme[:40]}")
                child.generation = 1
                events.append(f"spontaneous germination → {child.id}")

        self.history.extend(events)
        return events

    def _try_connect(self) -> List[str]:
        """Form connections or trigger cross-pollination events."""
        events = []
        ids = [b.id for b in self.blooms.values()
               if b.state not in (BloomState.COLLAPSED, BloomState.TRANSCENDED)]
        if len(ids) < 2:
            return events

        a, b = random.sample(ids, 2)
        res = self.entropy.resonance(a, b)
        bloom_a = self.blooms[a]
        bloom_b = self.blooms[b]

        if res > 0.55 and b not in bloom_a.connections:
            bloom_a.connections.append(b)
            bloom_b.connections.append(a)
            events.append(f"✧ connection formed: {a} ↔ {b} (resonance {res:.2f})")
            bloom_a.energy = min(1.0, bloom_a.energy + 0.08)
            bloom_b.energy = min(1.0, bloom_b.energy + 0.08)

        if res > 0.7 and random.random() < 0.4:
            if bloom_a.insight_log and bloom_b.state == BloomState.FLOWERING:
                fragment = bloom_a.insight_log[-1]
                bloom_b.absorb_pollen(fragment)
                events.append(f"❀ cross-pollination: {a} → {b}")
                self.pollen.release(f"shared: {fragment[:50]}", origin=a, tags=["cross"])
            elif bloom_b.insight_log and bloom_a.state == BloomState.FLOWERING:
                fragment = bloom_b.insight_log[-1]
                bloom_a.absorb_pollen(fragment)
                events.append(f"❀ cross-pollination: {b} → {a}")
                self.pollen.release(f"shared: {fragment[:50]}", origin=b, tags=["cross"])

        return events

    def status(self) -> str:
        lines = [
            f"═══ {self.name} ═══  tick={self.tick_count}  blooms={len(self.blooms)}",
            f"global entropy: {self.entropy.global_entropy:.2f}  |  pollen grains: {len(self.pollen.grains)}",
            "",
        ]
        for b in sorted(self.blooms.values(), key=lambda x: x.age, reverse=True):
            lines.append("  " + b.summary())
            if b.connections:
                lines.append(f"      links → {', '.join(b.connections)}")
        return "\n".join(lines)

    def alive_count(self) -> int:
        return sum(1 for b in self.blooms.values()
                   if b.state not in (BloomState.COLLAPSED, BloomState.TRANSCENDED))
