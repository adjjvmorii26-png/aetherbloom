#!/usr/bin/env python3
"""
AetherBloom Web Garden — lightweight live viewer.

Serves a dark, living page that shows the current lattice SVG,
bloom list, and recent events. The garden ticks in a background thread.

  python web_garden.py
  → open http://127.0.0.1:8765
"""

from __future__ import annotations
import argparse
import json
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse, parse_qs

from core.lattice import Lattice
from core.persistence import save_garden, load_garden
from viz.svg_lattice import render_svg


GARDEN: Lattice | None = None
LOCK = threading.Lock()
EVENTS: list[str] = []
RUNNING = True


HTML = """<!DOCTYPE html>
<html lang=\"en\">
<head>
<meta charset=\"utf-8\"/>
<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"/>
<title>AetherBloom — live garden</title>
<style>
  :root { --bg: #0d1117; --fg: #c9d1d9; --muted: #6e7681; --accent: #4ecdc4; --yellow: #f7c948; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--fg); font-family: ui-monospace, SFMono-Regular, Menlo, monospace; min-height: 100vh; }
  header { padding: 1.2rem 1.5rem; border-bottom: 1px solid #21262d; display: flex; justify-content: space-between; align-items: center; }
  header h1 { font-size: 1.1rem; color: var(--accent); font-weight: 600; }
  header .meta { color: var(--muted); font-size: 0.85rem; }
  main { display: grid; grid-template-columns: 1fr 320px; gap: 0; min-height: calc(100vh - 60px); }
  #viz { padding: 1rem; overflow: auto; display: flex; justify-content: center; align-items: flex-start; }
  #viz svg { max-width: 100%; height: auto; border-radius: 8px; }
  aside { border-left: 1px solid #21262d; padding: 1rem; overflow-y: auto; background: #010409; }
  aside h2 { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; color: var(--muted); margin-bottom: 0.8rem; }
  .bloom { padding: 0.5rem 0; border-bottom: 1px solid #161b22; font-size: 0.8rem; }
  .bloom .id { color: var(--accent); }
  .bloom .state { color: var(--yellow); }
  .bloom .seed { color: var(--muted); display: block; margin-top: 2px; }
  #events { margin-top: 1.5rem; }
  #events .ev { font-size: 0.75rem; color: var(--muted); padding: 0.25rem 0; border-bottom: 1px solid #161b22; }
  form { margin-top: 1.2rem; }
  form input { width: 100%; background: #0d1117; border: 1px solid #30363d; color: var(--fg); padding: 0.5rem; border-radius: 6px; font-family: inherit; font-size: 0.85rem; }
  form button { margin-top: 0.5rem; width: 100%; background: #21262d; border: 1px solid #30363d; color: var(--accent); padding: 0.5rem; border-radius: 6px; cursor: pointer; font-family: inherit; }
  form button:hover { background: #30363d; }
  @media (max-width: 800px) { main { grid-template-columns: 1fr; } aside { border-left: none; border-top: 1px solid #21262d; } }
</style>
</head>
<body>
<header>
  <h1>🌱 AetherBloom</h1>
  <div class=\"meta\" id=\"meta\">loading…</div>
</header>
<main>
  <section id=\"viz\"><div style=\"color:var(--muted);padding:2rem\">rendering lattice…</div></section>
  <aside>
    <h2>Blooms</h2>
    <div id=\"blooms\"></div>
    <div id=\"events\">
      <h2>Recent events</h2>
      <div id=\"evlist\"></div>
    </div>
    <form id=\"plant\">
      <h2 style=\"margin-top:1rem\">Plant a seed</h2>
      <input name=\"seed\" placeholder=\"an idea, a question…\" required maxlength=\"120\"/>
      <button type=\"submit\">Plant</button>
    </form>
  </aside>
</main>
<script>
async function refresh() {
  try {
    const r = await fetch('/api/state');
    const d = await r.json();
    document.getElementById('meta').textContent =
      d.name + ' · tick ' + d.tick + ' · alive ' + d.alive + ' · pollen ' + d.pollen;
    document.getElementById('viz').innerHTML = d.svg;
    const blooms = document.getElementById('blooms');
    blooms.innerHTML = d.blooms.map(b =>
      `<div class=\"bloom\"><span class=\"id\">${b.id}</span> <span class=\"state\">${b.state}</span>
       <span class=\"seed\">${b.seed}</span></div>`
    ).join('');
    document.getElementById('evlist').innerHTML = d.events.map(e =>
      `<div class=\"ev\">· ${e}</div>`
    ).join('');
  } catch (e) { console.warn(e); }
}
document.getElementById('plant').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const seed = ev.target.seed.value.trim();
  if (!seed) return;
  await fetch('/api/plant?seed=' + encodeURIComponent(seed), { method: 'POST' });
  ev.target.seed.value = '';
  refresh();
});
refresh();
setInterval(refresh, 1800);
</script>
</body>
</html>
"""


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in (\"/\", \"/index.html\"):
            self._html(HTML)
        elif parsed.path == \"/api/state\":
            self._json(self._state())
        elif parsed.path == \"/garden.svg\":
            self._svg()
        else:
            self.send_error(404)

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == \"/api/plant\":
            qs = parse_qs(parsed.query)
            seed = (qs.get(\"seed\") or [\"\"])[0].strip()
            if seed and GARDEN:
                with LOCK:
                    GARDEN.plant(seed)
                self._json({\"ok\": True, \"seed\": seed})
            else:
                self._json({\"ok\": False}, code=400)
        else:
            self.send_error(404)

    def _state(self) -> dict:
        with LOCK:
            if not GARDEN:
                return {\"name\": \"—\", \"tick\": 0, \"alive\": 0, \"pollen\": 0, \"blooms\": [], \"events\": [], \"svg\": \"\"}
            svg_path = Path(\"_web_lattice.svg\")
            render_svg(GARDEN, svg_path)
            svg = svg_path.read_text(encoding=\"utf-8\")
            blooms = []
            for b in sorted(GARDEN.blooms.values(), key=lambda x: -x.age):
                blooms.append({
                    \"id\": b.id,
                    \"state\": b.state.name,
                    \"seed\": b.seed[:60],
                    \"energy\": round(b.energy, 2),
                })
            return {
                \"name\": GARDEN.name,
                \"tick\": GARDEN.tick_count,
                \"alive\": GARDEN.alive_count(),
                \"pollen\": len(GARDEN.pollen.grains),
                \"blooms\": blooms,
                \"events\": EVENTS[-12:],
                \"svg\": svg,
            }

    def _html(self, body: str):
        data = body.encode(\"utf-8\")
        self.send_response(200)
        self.send_header(\"Content-Type\", \"text/html; charset=utf-8\")
        self.send_header(\"Content-Length\", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _json(self, obj, code=200):
        data = json.dumps(obj).encode(\"utf-8\")
        self.send_response(code)
        self.send_header(\"Content-Type\", \"application/json\")
        self.send_header(\"Content-Length\", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _svg(self):
        path = Path(\"_web_lattice.svg\")
        if path.exists():
            data = path.read_bytes()
            self.send_response(200)
            self.send_header(\"Content-Type\", \"image/svg+xml\")
            self.send_header(\"Content-Length\", str(len(data)))
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404)


def tick_loop(delay: float):
    global EVENTS
    while RUNNING:
        time.sleep(delay)
        with LOCK:
            if GARDEN is None:
                continue
            new_events = GARDEN.tick()
            if new_events:
                EVENTS.extend(new_events)
                EVENTS = EVENTS[-60:]


def main():
    global GARDEN, RUNNING
    parser = argparse.ArgumentParser(description=\"AetherBloom live web garden\")
    parser.add_argument(\"--port\", \"-p\", type=int, default=8765)
    parser.add_argument(\"--load\", \"-l\", default=None, help=\"Load garden JSON\")
    parser.add_argument(\"--delay\", \"-d\", type=float, default=1.4, help=\"Tick interval seconds\")
    parser.add_argument(\"--name\", default=\"web garden\")
    parser.add_argument(\"--seed\", \"-s\", action=\"append\", default=[])
    args = parser.parse_args()

    if args.load and Path(args.load).exists():
        GARDEN = load_garden(args.load)
        print(f\"Restored garden from {args.load}\")
    else:
        GARDEN = Lattice(name=args.name)
        seeds = args.seed or [
            \"what if silence had a temperature?\",
            \"the geometry of almost-touching\",
            \"a clock that runs on forgotten names\",
        ]
        for s in seeds:
            GARDEN.plant(s)
        print(f\"Planted {len(seeds)} seed(s)\")

    t = threading.Thread(target=tick_loop, args=(args.delay,), daemon=True)
    t.start()

    server = HTTPServer((\"127.0.0.1\", args.port), Handler)
    print(f\"🌱 AetherBloom web garden → http://127.0.0.1:{args.port}\")
    print(\"   ctrl-c to stop (auto-saves)\")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print(\"\\nStopping…\")
    finally:
        RUNNING = False
        if GARDEN:
            p = save_garden(GARDEN, \"garden_state.json\")
            print(f\"Saved → {p}\")
            render_svg(GARDEN, \"garden_lattice.svg\")
            print(\"SVG → garden_lattice.svg\")


if __name__ == \"__main__\":
    main()
