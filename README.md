# Mplayer.com Revival

[![CI](https://github.com/Blizz127/Mplayer.com-Revival/actions/workflows/ci.yml/badge.svg)](https://github.com/Blizz127/Mplayer.com-Revival/actions/workflows/ci.yml)

A community preservation project to bring back **[Mplayer.com](https://en.wikipedia.org/wiki/MPlayer.com)** — the
pioneering online gaming, chat, and voice service operated by Mpath Interactive from **late 1996 until 2001**, when
it was absorbed into GameSpy and shut down.

The goal is the same one the [TEN](https://en.wikipedia.org/wiki/Total_Entertainment_Network),
[OpenSpy/RetroSpy](https://github.com/GameProgressive/RetroSpyServer), and Heat.net revivals pursued: **stand the
dead service back up** so the original software lives again — and, on top of that, offer a **modernized client** that
runs natively on Windows 11 and beyond.

> **Status:** 🟡 Phase 0 — Preservation & scaffolding. No servers are live yet. See [docs/ROADMAP.md](docs/ROADMAP.md).

---

## How a revival like this works

Late-90s online services were just a **client** talking to a set of **central servers** over hardcoded hostnames.
Those servers are gone, so the client connects to nothing. We bring it back the proven way:

1. **Preserve** the original client. ✅ (`preservation/` — the original Mplayer installer is archived here.)
2. **Reverse-engineer** the wire protocol the client speaks (login, lobby/chat, matchmaking, voice).
3. **Reimplement** the servers from those notes (this repo's `server/`).
4. **Redirect** the client's hardcoded hostnames to our servers via DNS or a `hosts` file — *no binary patching
   required* (`tools/redirect/`). This is the same trick OpenSpy uses to revive GameSpy titles.

The reverse-engineered protocol is the **shared contract**, which lets us pursue two client tracks at once:

| Track | What it is | Runs on Win 11? |
| --- | --- | --- |
| **Faithful** | The *original* Mplayer client, pointed at our servers. | Via compatibility shims (see below) |
| **Modernized** | A *new, cross-platform* client that speaks the same protocol. | ✅ Natively (and macOS/Linux) |

Both are first-class goals. See [docs/client-modernization.md](docs/client-modernization.md).

---

## Repository layout

```
.
├── docs/                  Architecture, roadmap, and reverse-engineering notes
│   ├── ARCHITECTURE.md       Original service design + our revival design
│   ├── ROADMAP.md            Phased plan (you are here: Phase 0)
│   ├── PROTOCOL.md           Wire-protocol notes (filled in during Phase 1)
│   ├── client-modernization.md  Faithful-vs-modern client tracks; Win11 path
│   └── installer-analysis.md    What we know about the preserved installer
├── preservation/          The original client, archived with checksums
├── server/                Python reimplementation of the Mplayer servers
│   └── mplayer_server/       Currently: a logging stub server for protocol capture
├── tools/
│   ├── client_inspect.py     Pull hostnames/ports/strings from the extracted client
│   └── redirect/             Helpers to point the original client at our servers
└── web/                   Landing + service-status page (python web/serve.py)
```

---

## Quick start (protocol capture stub)

The first practical tool is a **logging stub server**: it listens on the ports the client tries to reach and
hex-dumps every byte it sends, so we can document the protocol. Pure Python standard library — no dependencies.

```bash
cd server
# Listen on some TCP and UDP ports and log everything the client sends:
python -m mplayer_server --tcp 7000 7777 --udp 6500

# Run the tests:
python -m pytest
```

Point the original client at `127.0.0.1` (see `tools/redirect/`) and the captures land in `server/captures/`.
Once we know the real hostnames and ports (Phase 1), they get recorded in `tools/redirect/hostnames.txt` and
`docs/PROTOCOL.md`.

### See the landing page

```bash
python web/serve.py        # -> http://127.0.0.1:8000  (landing + service-status board)
```

### Inspect an extracted client (Phase 1)

After running the original installer on Windows (or otvdm) and extracting the client, auto-pull its network
indicators:

```bash
python tools/client_inspect.py /path/to/extracted/client --hostnames-out found.txt
```

---

## Contributing & legal

This is a **clean-room preservation effort**. Mplayer.com and its client are the property of their respective
rights holders (Mpath Interactive → HearMe → GameSpy/IGN lineage); they are preserved here as **abandonware** for
historical and interoperability purposes. We do not redistribute anything beyond what is necessary for preservation,
and the reimplemented servers are written from observed behavior, not leaked source. See
[CONTRIBUTING.md](CONTRIBUTING.md) before submitting protocol work.

Project code is licensed under the **GNU GPL v3** ([LICENSE](LICENSE)). Preserved third-party binaries under
`preservation/` are **not** covered by that license and remain the property of their owners.
