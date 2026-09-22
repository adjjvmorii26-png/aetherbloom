"""Garden persistence — save and load living lattices as JSON."""

from __future__ import annotations
import json
import time
from pathlib import Path
from typing import Optional

from .bloom import Bloom, BloomState
from .lattice import Lattice
from .pollen import PollenGrain


def save_garden(lattice: Lattice, path: str | Path) -> Path:
    """Serialize the entire garden to a JSON file."""
    path = Path(path)
    data = {
        "format": "aetherbloom-v1",
        "name": lattice.name,
        "tick_count": lattice.tick_count,
        "created_at": lattice.created_at,
        "saved_at": time.time(),
        "global_entropy": lattice.entropy.global_entropy,
        "blooms": [],
        "pollen": [],
        "history_tail": lattice.history[-100:],
    }

    for b in lattice.blooms.values():
        data["blooms"].append({
            "id": b.id,
            "seed": b.seed,
            "state": b.state.name,
            "age": b.age,
            "generation": b.generation,
            "energy": round(b.energy, 4),
            "insight_log": b.insight_log[-40:],
            "connections": b.connections,
            "created_at": b.created_at,
            "last_mutation": b.last_mutation,
            "archetype": b.archetype,
            "entropy": lattice.entropy.bloom_entropy.get(b.id, 0.4),
            "novelty": lattice.entropy.bloom_novelty.get(b.id, 0.5),
        })

    for g in lattice.pollen.grains:
        data["pollen"].append({
            "content": g.content,
            "origin_bloom": g.origin_bloom,
            "strength": round(g.strength, 4),
            "created_at": g.created_at,
            "tags": g.tags,
        })

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")
    return path


def load_garden(path: str | Path) -> Lattice:
    """Rehydrate a garden from JSON. Returns a fully living Lattice."""
    path = Path(path)
    data = json.loads(path.read_text(encoding="utf-8"))

    if data.get("format") != "aetherbloom-v1":
        raise ValueError(f"Unsupported garden format: {data.get('format')}")

    lattice = Lattice(name=data.get("name", "restored garden"))
    lattice.tick_count = data.get("tick_count", 0)
    lattice.created_at = data.get("created_at", time.time())
    lattice.history = data.get("history_tail", [])
    lattice.entropy.global_entropy = data.get("global_entropy", 0.35)

    for bd in data.get("blooms", []):
        try:
            state = BloomState[bd["state"]]
        except KeyError:
            state = BloomState.FLOWERING

        bloom = Bloom(
            id=bd["id"],
            seed=bd["seed"],
            state=state,
            age=bd.get("age", 0),
            generation=bd.get("generation", 0),
            energy=bd.get("energy", 0.8),
            insight_log=bd.get("insight_log", []),
            connections=bd.get("connections", []),
            created_at=bd.get("created_at", time.time()),
            last_mutation=bd.get("last_mutation"),
            archetype=bd.get("archetype"),
        )
        lattice.blooms[bloom.id] = bloom
        lattice.entropy.bloom_entropy[bloom.id] = bd.get("entropy", 0.4)
        lattice.entropy.bloom_novelty[bloom.id] = bd.get("novelty", 0.5)

    for pd in data.get("pollen", []):
        grain = PollenGrain(
            content=pd["content"],
            origin_bloom=pd["origin_bloom"],
            strength=pd.get("strength", 0.5),
            created_at=pd.get("created_at", time.time()),
            tags=pd.get("tags", []),
        )
        lattice.pollen.grains.append(grain)

    return lattice
