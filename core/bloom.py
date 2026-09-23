"""A single Bloom — an autonomous thought organism."""

from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Optional, Dict
import random
import uuid
import time


class BloomState(Enum):
    SEED = auto()
    SPROUTING = auto()
    FLOWERING = auto()
    MUTATING = auto()
    SYMBIOTIC = auto()
    WILTING = auto()
    TRANSCENDED = auto()
    COLLAPSED = auto()


MUTATION_FRAGMENTS = [
    "echoes of forgotten geometry",
    "the quiet violence of stillness",
    "gravity as a form of longing",
    "time folding into itself",
    "a question that refuses to end",
    "light that remembers being shadow",
    "the architecture of almost",
    "silence learning to speak",
    "patterns that dream of chaos",
    "the last color before night",
    "memory of a future that never arrived",
    "entropy wearing a mask of order",
    "a door that opens only inward",
    "the weight of unasked questions",
    "stars that forgot how to burn",
]

GROWTH_VERBS = [
    "reaches toward", "dissolves into", "remembers", "forgets",
    "entangles with", "splits from", "whispers to", "absorbs",
    "refracts", "becomes the opposite of", "circles around",
]


@dataclass
class Bloom:
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    seed: str = "an unnamed thought"
    state: BloomState = BloomState.SEED
    age: int = 0
    generation: int = 0
    energy: float = 1.0
    insight_log: List[str] = field(default_factory=list)
    connections: List[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    last_mutation: Optional[str] = None
    archetype: Optional[str] = None

    def __post_init__(self):
        if not self.insight_log:
            self.insight_log.append(f"seed planted: {self.seed}")

    def grow(self, pollen_nearby: List[str] = None, entropy: float = 0.4) -> Optional[str]:
        self.age += 1
        pollen_nearby = pollen_nearby or []

        if self.state == BloomState.COLLAPSED or self.state == BloomState.TRANSCENDED:
            return None

        self.energy = max(0.0, self.energy - 0.03 + random.uniform(0, 0.05))

        if self.state == BloomState.SEED and self.age > 2:
            self.state = BloomState.SPROUTING
            insight = f"sprouts: {self.seed} begins to unfold"
            self.insight_log.append(insight)
            return insight

        if self.state == BloomState.SPROUTING and self.age > 6:
            self.state = BloomState.FLOWERING
            try:
                from .llm_mutate import mutate_insight
                frag = mutate_insight(self.seed, self.insight_log, entropy)
            except Exception:
                frag = random.choice(MUTATION_FRAGMENTS)
            insight = f"flowers: {frag}"
            self.insight_log.append(insight)
            return insight

        if self.state == BloomState.FLOWERING:
            if entropy > 0.75 and random.random() < 0.3:
                return self._mutate(entropy=entropy)
            if self.energy < 0.25:
                self.state = BloomState.WILTING
                return "begins to wilt under low energy"
            if random.random() < 0.4:
                frag = random.choice(MUTATION_FRAGMENTS)
                if pollen_nearby and random.random() < 0.5:
                    frag = f"{random.choice(GROWTH_VERBS)} {random.choice(pollen_nearby)[:40]}"
                insight = f"grows: {frag}"
                self.insight_log.append(insight)
                return insight

        if self.state == BloomState.MUTATING:
            self.state = BloomState.FLOWERING
            return self.last_mutation

        if self.state == BloomState.WILTING:
            if self.energy > 0.5:
                self.state = BloomState.FLOWERING
                return "recovers from wilting"
            if self.age > 40 or self.energy < 0.05:
                self.state = BloomState.COLLAPSED
                return "collapses into silence"

        return None

    def _mutate(self, entropy: float = 0.5) -> str:
        self.state = BloomState.MUTATING
        try:
            from .llm_mutate import mutate_insight
            new_direction = mutate_insight(self.seed, self.insight_log, entropy)
        except Exception:
            new_direction = random.choice(MUTATION_FRAGMENTS)
        self.last_mutation = f"mutates → {new_direction}"
        self.insight_log.append(self.last_mutation)
        self.energy = min(1.0, self.energy + 0.3)
        return self.last_mutation

    def try_transcend(self) -> bool:
        if self.age > 25 and self.energy > 0.7 and random.random() < 0.08:
            self.state = BloomState.TRANSCENDED
            self.archetype = self.insight_log[-1] if self.insight_log else self.seed
            return True
        return False

    def absorb_pollen(self, content: str) -> None:
        self.insight_log.append(f"absorbs pollen: {content[:60]}")
        self.energy = min(1.0, self.energy + 0.12)

    def summary(self) -> str:
        return (
            f"[{self.id}] {self.state.name:12} age={self.age:3} "
            f"E={self.energy:.2f} gen={self.generation} | {self.seed[:40]}"
        )
