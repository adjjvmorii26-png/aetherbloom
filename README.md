# 🌱 AetherBloom

**A living digital garden of autonomous thought-blooms.**

You plant seeds (ideas, questions, fragments).  
Each seed germinates into a **Bloom** — a small autonomous agent that:

- grows by exploring its own concept space  
- mutates under entropy pressure  
- leaves pollen trails that influence neighbors  
- forms symbiotic clusters or competes for attention energy  
- eventually dies, seeds new generations, or transcends into a persistent archetype

The garden itself has **physics**: novelty budgets, resonance fields, and an ever-shifting lattice of connections.  
Watch it evolve in the terminal or as generative SVG art.

---

## Why this exists

Most AI tools are conversation endpoints.  
AetherBloom is a **place** — a persistent, growing ecology of ideas that lives even when you step away.

It is deliberately lightweight, local-first, and weird on purpose.

## Quick start

```bash
# clone
git clone https://github.com/adjjvmorii26-png/aetherbloom.git
cd aetherbloom

# pure python, zero heavy deps
python -m aetherbloom.garden

# or plant a custom seed
python -m aetherbloom.garden --seed "what if gravity was a conversation?"
```

## Core concepts

| Concept | Meaning |
|---------|---------|
| **Seed** | A short prompt or idea you plant |
| **Bloom** | An autonomous agent that grows from a seed |
| **Pollen** | Fragments of insight a bloom leaves behind |
| **Resonance** | How strongly two blooms attract or repel |
| **Entropy budget** | How much chaos a bloom is allowed before it collapses or mutates |
| **Lattice** | The living graph of all blooms and their connections |

## Architecture (v0.1)

```
aetherbloom/
├── core/
│   ├── bloom.py        # single bloom agent
│   ├── lattice.py      # the garden graph + physics
│   ├── entropy.py      # novelty & budget systems
│   └── pollen.py       # trails & inheritance
├── blooms/             # specialized bloom types (future)
├── viz/                # terminal + SVG renderers
├── examples/
└── garden.py           # main entry point
```

## Roadmap (living)

- [x] Core bloom + lattice physics
- [x] Terminal garden viewer
- [ ] SVG generative art export
- [ ] Cross-pollination events
- [ ] Persistent garden state (JSON / SQLite)
- [ ] Optional LLM-backed mutation (when API key present)
- [ ] Web garden viewer (lightweight)
- [ ] Multiplayer pollen sharing

## Philosophy

> Ideas want to live.  
> Give them a garden, not a chat window.

AetherBloom is an experiment in **emergent thought ecology**.

---

Made with deliberate weirdness.  
Plant something strange.
