# Web

The public face of the revival: a landing + **service-status** page.

```bash
python web/serve.py            # -> http://127.0.0.1:8000
python web/serve.py --port 9000 --host 0.0.0.0
```

Static files live in [`public/`](public/) (`index.html` + `style.css`), served by a tiny stdlib HTTP server
(`serve.py`) — no dependencies, no build step.

## Status

This is an early landing/status page. The "Service status" board is **hand-updated** as milestones land; later it
will be wired to report the real servers' health. The full mplayer.com community site (accounts, news, the in-browser
modern client) is Phase 4 — see [../docs/ROADMAP.md](../docs/ROADMAP.md).

Marks like "Mplayer" belong to their respective owners; this is an unaffiliated preservation project.
