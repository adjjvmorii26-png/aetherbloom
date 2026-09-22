"""Pollen — the trails of insight blooms leave behind."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time
import random


@dataclass
class PollenGrain:
    content: str
    origin_bloom: str
    strength: float = 1.0
    created_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)

    def decay(self, rate: float = 0.015) -> None:
        self.strength = max(0.0, self.strength - rate)


@dataclass
class PollenTrail:
    """Collective memory of the garden."""
    grains: List[PollenGrain] = field(default_factory=list)
    max_grains: int = 200

    def release(self, content: str, origin: str, tags: Optional[List[str]] = None) -> None:
        grain = PollenGrain(
            content=content.strip()[:280],
            origin_bloom=origin,
            tags=tags or [],
            strength=1.0 + random.random() * 0.4,
        )
        self.grains.append(grain)
        if len(self.grains) > self.max_grains:
            # keep the strongest
            self.grains.sort(key=lambda g: g.strength, reverse=True)
            self.grains = self.grains[: self.max_grains]

    def tick(self) -> None:
        for g in self.grains:
            g.decay()
        self.grains = [g for g in self.grains if g.strength > 0.08]

    def nearby(self, bloom_id: str, limit: int = 5) -> List[PollenGrain]:
        """Return strongest grains not from this bloom."""
        candidates = [g for g in self.grains if g.origin_bloom != bloom_id]
        candidates.sort(key=lambda g: g.strength, reverse=True)
        return candidates[:limit]

    def strongest_theme(self) -> Optional[str]:
        if not self.grains:
            return None
        return max(self.grains, key=lambda g: g.strength).content
