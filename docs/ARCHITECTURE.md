# Architecture

This document describes (a) what we know of the **original** Mplayer.com service and (b) the **revival**
architecture we are building. Treat the "original" section as a working model to be confirmed/corrected during
reverse-engineering (Phase 1) — anything unverified is marked _(unconfirmed)_.

---

## 1. The original service (1996–2001)

Mplayer.com was built by **Mpath Interactive** (Cupertino, CA). It was a free, ad-supported online gaming community
and one of the first to combine matchmaking with **real-time voice chat**. Its backend technology was branded
**POP.X** and licensed to third parties (EA, Fujitsu) to build their own communities.

### Client

A Windows application (the artifact preserved in `preservation/`). Notable features:

- **Login / account** screen.
- **Lobby**: hierarchical "rooms" / channels organized by game and topic, with text chat and the service's
  trademark **animated emotes / "gizmos."**
- **Matchmaking**: browse and create hosted game sessions; the service launched the actual game and brokered the
  network connection between players.
- **Voice chat**: real-time voice over the lobby, later spun out as **Roger Wilco** (HearMe).

### Server side (the "POP" servers) — _working model_

Period services of this kind decomposed into a handful of cooperating servers. Our working assumption for Mplayer:

| Component | Responsibility | Transport _(unconfirmed)_ |
| --- | --- | --- |
| **Auth / login** | Authenticate the user, hand back a session/token, route to a lobby server. | TCP |
| **Directory / lobby** | Room list, presence, text chat, emotes, who's-online. | TCP (text or binary framed) |
| **Matchmaking** | Game catalog, create/join/list game sessions, launch parameters. | TCP |
| **Game connection broker** | Get two+ players' game traffic to each other (relay and/or NAT facilitation; possibly **IPX tunneling** for LAN-only titles, à la Kali). | UDP + TCP |
| **Voice** | Mix/relay real-time voice for a room or game. | UDP |
| **Web** | The mplayer.com website, news, downloads, account web pages. | HTTP |

### How games actually connected

Many late-90s titles were **LAN-only (IPX/SPX)** or used direct-IP/DirectPlay. Services made them work over the
Internet by either:

- **Tunneling IPX over UDP** (what Kali did), presenting a virtual LAN to the game; or
- **Brokering direct IP** sessions (matchmaking gives each side the other's address; the service may relay if a
  direct connection fails).

Which approach Mplayer used per game is a Phase 1/Phase 3 research item.

---

## 2. The revival architecture (what we're building)

```
        ┌──────────────────────────────┐
        │   Original Mplayer client     │   (faithful track — preserved binary)
        │            OR                 │
        │   Modernized client (new)     │   (modern track — cross-platform)
        └───────────────┬──────────────┘
                        │  hardcoded hostnames (*.mplayer.com / *.mpath.com)
                        ▼
        ┌──────────────────────────────┐
        │   Redirection layer            │   tools/redirect/
        │   DNS override or hosts file   │   → points old hostnames at our servers
        └───────────────┬──────────────┘
                        ▼
   ┌───────────────────────────────────────────────────────┐
   │                 server/  (Python)                      │
   │                                                        │
   │  Phase 1:  logging stub  ── captures raw bytes ──┐     │
   │                                                  ▼     │
   │  Phase 2:  auth ──▶ lobby/chat ──▶ matchmaking         │
   │  Phase 3:  game connection broker (relay / IPX tunnel) │
   │  Phase 4:  voice relay + web frontend                  │
   └───────────────────────────────────────────────────────┘
```

### Design principles

1. **Protocol-first.** Every server is built from documented observations in `docs/PROTOCOL.md`. We capture before
   we implement (hence the logging stub is the very first component).
2. **No binary patching for the faithful track.** We prefer hostname redirection (DNS / `hosts`) so the original,
   unmodified client connects. Patching is a fallback only where the client can't be redirected (e.g. an IP literal
   baked into the binary).
3. **One protocol, two clients.** The faithful and modernized clients are both just *speakers* of the same
   reverse-engineered protocol, so server work benefits both.
4. **Stdlib-first Python.** Start dependency-free (asyncio) for fast iteration during RE; introduce libraries only
   when a component clearly needs them. Hot paths (e.g. voice/relay) can be optimized or ported later.

### Server technology

- **Language:** Python 3.11+ (asyncio). Mirrors the approach of GameSpy's
  [UniSpy](https://github.com/GameProgressive/UniSpyServer) revival — quick to prototype binary/text protocol
  parsers and stub endpoints.
- **Process model:** each logical server (auth, lobby, matchmaking, …) is an asyncio service that can run in one
  process for development or be split out later.
- **Storage:** TBD when accounts land (Phase 2). Likely SQLite for development; Postgres if/when hosted.

See [client-modernization.md](client-modernization.md) for the two client tracks and the Windows 11 story, and
[ROADMAP.md](ROADMAP.md) for sequencing.
