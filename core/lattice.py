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

        # 1. age every bloom + collect insights
        active_ids = list(self.blooms.keys())
        for bid in active_ids:
            bloom = self.blooms[bid]
            if bloom.state in (BloomState.COLLAPSED, BloomState.TRANSCENDED):
                continue

            # gather nearby pollen content
            nearby = [g.content for g in self.pollen.nearby(bid, limit=3)]
            e = self.entropy.tick(bid, activity=0.1 if nearby else 0.05)

            insight = bloom.grow(pollen_nearby=nearby, entropy=e)
            if insight:
                events.append(f"{bloom.id}: {insight}")
                # release some pollen
                if random.random() < 0.45:
                    self.pollen.release(insight, origin=bid)

            # rare transcendence
            if bloom.try_transcend():
                events.append(f"✦ {bloom.id} transcended → archetype: {bloom.archetype}")
                self.pollen.release(f"ARCHETYPE: {bloom.archetype}", origin=bid, tags=["transcendent"])

            # forced mutation from high entropy
            if self.entropy.should_mutate(bid) and bloom.state == BloomState.FLOWERING:
                insight = bloom._mutate()
                events.append(f"{bloom.id}: {insight}")
                self.entropy.inject_novelty(bid, 0.4)

            # collapse
            if self.entropy.should_collapse(bid):
                bloom.state = BloomState.COLLAPSED
                events.append(f"{bloom.id}: collapsed under entropy overload")

        # 2. pollen decay
        self.pollen.tick()

        # 3. occasional cross-pollination / connection formation
        if len(self.blooms) >= 2 and random.random() < 0.25:
            events.extend(self._try_connect())

        # 4. spontaneous new seed from strong pollen (rare)
        if self.tick_count > 15 and random.random() < 0.06:
            theme = self.pollen.strongest_theme()
            if theme:
                child = self.plant(f"echo of: {theme[:40]}")
                child.generation = 1
                events.append(f"spontaneous germination → {child.id}")

        self.history.extend(events)
        return events

    def _try_connect(self) -> List[str]:
        """Form or strengthen connections based on resonance."""
        events = []
        ids = [b.id for b in self.blooms.values()
               if b.state not in (BloomState.COLLAPSED, BloomState.TRANSCENDED)]
        if len(ids) < 2:
            return events

        a, b = random.sample(ids, 2)
        res = self.entropy.resonance(a, b)
        if res > 0.55:
            bloom_a = self.blooms[a]
            bloom_b = self.blooms[b]
            if b not in bloom_a.connections:
                bloom_a.connections.append(b)
                bloom_b.connections.append(a)
                events.append(f"✧ connection formed: {a} ↔ {b} (resonance {res:.2f})")
                # exchange a little energy
                bloom_a.energy = min(1.0, bloom_a.energy + 0.08)
                bloom_b.energy = min(1.0, bloom_b.energy + 0.08)
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
