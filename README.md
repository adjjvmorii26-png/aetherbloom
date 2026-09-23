# 🌱 AetherBloom

**A living digital garden of autonomous thought-blooms.**

You plant seeds (ideas, questions, fragments).  
Each seed germinates into a **Bloom** — a small autonomous agent that:

- grows by exploring its own concept space  
- mutates under entropy pressure  
- leaves pollen trails that influence neighbors  
- forms symbiotic clusters or competes for attention energy  
- cross-pollinates insights with resonant neighbors  
- eventually dies, seeds new generations, or transcends into a persistent archetype

The garden itself has **physics**: novelty budgets, resonance fields, and an ever-shifting lattice of connections.  
It remembers. You can save it, leave, and return later.  
It draws itself as generative SVG art.  
It can run in the terminal or as a live web garden.

---

## Quick start

```bash
git clone https://github.com/adjjvmorii26-png/aetherbloom.git
cd aetherbloom

# terminal garden (pure python, zero deps)
python garden.py

# plant your own seeds
python garden.py \
  --seed "what if gravity was a conversation?" \
  --seed "the last color before night"

# run 40 ticks then auto-save + SVG
python garden.py --ticks 40 --delay 0.4

# restore a previous garden
python garden.py --load garden_state.json
```

### Live web garden

```bash
python web_garden.py
# → open http://127.0.0.1:8765
```

Watch blooms grow in real time, plant new seeds from the browser, and see the lattice redraw itself.

### Optional LLM mutations

If you set any of these environment variables, blooms will request richer mutations from an LLM (falls back to built-in poetry otherwise):

```bash
export XAI_API_KEY=...      # preferred (Grok)
# or OPENAI_API_KEY=...
# or ANTHROPIC_API_KEY=...

python garden.py --ticks 30
```

No extra packages required — uses the standard library.

## Core concepts

| Concept | Meaning |
|---------|---------|
| **Seed** | A short prompt or idea you plant |
| **Bloom** | An autonomous agent that grows from a seed |
| **Pollen** | Fragments of insight a bloom leaves behind |
| **Resonance** | How strongly two blooms attract or repel |
| **Cross-pollination** | Direct transfer of insight between resonant blooms |
| **Entropy budget** | How much chaos a bloom is allowed before it collapses or mutates |
| **Lattice** | The living graph of all blooms and their connections |
| **Transcendence** | Rare event: a bloom becomes a permanent archetype |

## Architecture

```
aetherbloom/
├── core/
│   ├── bloom.py         # single bloom agent + lifecycle
│   ├── lattice.py       # garden graph + physics + cross-pollination
│   ├── entropy.py       # novelty & budget systems
│   ├── pollen.py        # trails & inheritance
│   ├── persistence.py   # JSON save / load
│   └── llm_mutate.py    # optional LLM-backed mutations
├── viz/
│   └── svg_lattice.py   # generative SVG renderer
├── garden.py            # terminal CLI
├── web_garden.py        # live web viewer (stdlib HTTP server)
└── examples/
```

## Roadmap

- [x] Core bloom + lattice physics
- [x] Terminal garden viewer
- [x] Cross-pollination events
- [x] Persistent garden state (JSON)
- [x] SVG generative art export
- [x] Optional LLM-backed mutation
- [x] Lightweight web garden viewer
- [ ] Multiplayer pollen sharing
- [ ] Bloom archetypes as reusable seeds

## Philosophy

> Ideas want to live.  
> Give them a garden, not a chat window.

AetherBloom is an experiment in **emergent thought ecology**.

---

Made with deliberate weirdness.  
Plant something strange.
