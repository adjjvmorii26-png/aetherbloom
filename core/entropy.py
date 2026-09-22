"""Entropy field — the invisible physics that keeps the garden alive and strange."""

from __future__ import annotations
import math
import random
from dataclasses import dataclass, field
from typing import Dict


@dataclass
class EntropyField:
    """
    Global and per-bloom entropy budgets.
    Too little entropy → stagnation (bloom freezes).
    Too much → collapse or violent mutation.
    """
    global_entropy: float = 0.35          # 0..1 background chaos
    novelty_decay: float = 0.92           # how fast novelty fades
    mutation_threshold: float = 0.78      # above this → forced mutation
    collapse_threshold: float = 0.95      # above this → bloom dies or splits

    # per-bloom tracking
    bloom_entropy: Dict[str, float] = field(default_factory=dict)
    bloom_novelty: Dict[str, float] = field(default_factory=dict)

    def register(self, bloom_id: str, initial: float = 0.4) -> None:
        self.bloom_entropy[bloom_id] = initial
        self.bloom_novelty[bloom_id] = 1.0

    def tick(self, bloom_id: str, activity: float = 0.1) -> float:
        """Advance entropy for one bloom. Returns current entropy."""
        if bloom_id not in self.bloom_entropy:
            self.register(bloom_id)

        e = self.bloom_entropy[bloom_id]
        # activity adds chaos, time slowly pulls toward global
        e = e * 0.97 + activity * 0.15 + self.global_entropy * 0.03
        e = max(0.05, min(1.0, e + random.gauss(0, 0.02)))
        self.bloom_entropy[bloom_id] = e

        # novelty decays
        self.bloom_novelty[bloom_id] *= self.novelty_decay
        return e

    def inject_novelty(self, bloom_id: str, amount: float = 0.3) -> None:
        if bloom_id in self.bloom_novelty:
            self.bloom_novelty[bloom_id] = min(1.0, self.bloom_novelty[bloom_id] + amount)

    def should_mutate(self, bloom_id: str) -> bool:
        return self.bloom_entropy.get(bloom_id, 0) > self.mutation_threshold

    def should_collapse(self, bloom_id: str) -> bool:
        return self.bloom_entropy.get(bloom_id, 0) > self.collapse_threshold

    def resonance(self, a: str, b: str) -> float:
        """How much two blooms attract (0..1). Higher when entropy levels are similar."""
        ea = self.bloom_entropy.get(a, 0.5)
        eb = self.bloom_entropy.get(b, 0.5)
        diff = abs(ea - eb)
        return max(0.0, 1.0 - diff * 1.8) * (0.5 + 0.5 * random.random())
