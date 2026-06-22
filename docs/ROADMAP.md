# Roadmap

Phased plan for reviving Mplayer.com. Checkboxes are living state — tick them as work lands. "Faithful" = original
client connects again; "Modern" = new cross-platform client. The two share the reverse-engineered protocol, so most
server work serves both.

---

## Phase 0 — Preservation & scaffolding  🟡 _in progress_

Foundation so the real work has a home.

- [x] Decide approach (faithful + modernized client) and stack (Python).
- [x] Archive the original installer with checksums (`preservation/`).
- [x] Document the known architecture and this roadmap (`docs/`).
- [x] Logging stub server for protocol capture (`server/mplayer_server/`).
- [x] Hostname-redirect helper + hostname registry (`tools/redirect/`).
- [x] Client inspector (`tools/client_inspect.py`) — auto-extracts hostnames/ports/strings from the client.
- [x] Landing + service-status page (`web/`).
- [x] CI: run tests on every push (`.github/workflows/ci.yml`).
- [x] Confirmed extraction can't be done in a Linux container (payload fully compressed; Wine uninstallable) — it's
      a Windows-side step. See `docs/installer-analysis.md`.
- [ ] Migrate preserved binaries to Git LFS once `git lfs` is available (see `preservation/README.md`).

## Phase 1 — Protocol reverse-engineering  🔴 _next; needs a Windows test bench_

Learn exactly what the client says to the servers. **This is the gating phase** — everything downstream depends on it.

- [ ] **Extract the client.** Run the 16-bit installer in a 16-bit-capable environment (32-bit Windows VM, or
      [otvdm/winevdm](https://github.com/otya128/winevdm)). Catalog the installed files (EXEs, DLLs, INIs).
- [ ] **Find the hostnames/ports.** Pull hardcoded `*.mplayer.com` / `*.mpath.com` names and ports from the client
      binaries and INI/registry settings. Record them in `tools/redirect/hostnames.txt` and `docs/PROTOCOL.md`.
- [ ] **Capture traffic.** Redirect those hostnames to the logging stub; drive the client (launch, login attempt,
      lobby) and hex-dump everything it sends.
- [ ] **Document the framing.** Message boundaries, headers, opcodes, endianness, string encoding → `docs/PROTOCOL.md`.
- [ ] **Decode the login handshake** end to end (the first thing a server must answer).

## Phase 2 — Core servers  🔴

Make the client get *past the login screen and into a room*.

- [ ] **Auth/login server** — answer the handshake so the client authenticates against us.
- [ ] **Accounts** — registration + persistence (SQLite to start).
- [ ] **Directory/lobby server** — room list, presence, join/leave.
- [ ] **Text chat** (and emotes/"gizmos" if in scope).
- [ ] Milestone: an original client logs in and chats in a room. 🎯

## Phase 3 — Matchmaking & game connections  🔴

Make people actually *play*.

- [ ] **Matchmaking server** — game catalog, create/join/list sessions, launch parameters.
- [ ] **Connection broker** — relay and/or NAT facilitation between players.
- [ ] **IPX-over-UDP tunneling** for LAN-only titles (Kali-style), if required by the catalog.
- [ ] Milestone: two clients launch a supported game and play. 🎯

## Phase 4 — Voice, web, and the modern client  🔴

- [ ] **Voice relay** (UDP) for room/game voice chat.
- [ ] **mplayer.com web frontend** — landing page, news, downloads, account pages.
- [ ] **Modernized client** — a cross-platform client speaking the protocol, native on Windows 11 (+macOS/Linux).
      See [client-modernization.md](client-modernization.md).
- [ ] Hosting, anti-abuse, and a public test deployment.

---

## Cross-cutting

- **Windows 11 (faithful track):** the original *installer* is 16-bit and won't run on 64-bit Win11 directly — use
  a 32-bit VM or otvdm to extract/run. Whether the *client itself* is 32-bit (and thus shim-runnable on Win11 x64)
  is confirmed in Phase 1. Details in [client-modernization.md](client-modernization.md).
- **Legal/clean-room:** observed-behavior reimplementation only; see [../CONTRIBUTING.md](../CONTRIBUTING.md).

## Immediate next steps

1. Set up a Windows test bench (32-bit VM or otvdm) and **extract the client** from the preserved installer.
2. Record the client's hostnames/ports → `tools/redirect/hostnames.txt`.
3. Capture the **login handshake** against the logging stub and start `docs/PROTOCOL.md`.
