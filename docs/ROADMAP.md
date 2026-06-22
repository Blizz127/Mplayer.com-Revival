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

## Phase 1 — Protocol reverse-engineering  🔴 _next — bench guide ready_

Learn exactly what the client says to the servers. **This is the gating phase** — everything downstream depends on it.
Full walkthrough: **[win98-bench.md](win98-bench.md)** (a period Windows 98 box, like the TEN project).

- [ ] **Set up the bench.** Win98 box + a capture host on the same LAN running our Python tools.
- [ ] **Install the client** from `preservation/client/MplayerInstaller.exe` on the Win98 box.
- [ ] **Discover hostnames.** Point Win98's DNS at the capture host's `mplayer_server.dns_stub`; launch the client
      and read off every hostname it looks up. Record them in `tools/redirect/hostnames.txt` and `docs/PROTOCOL.md`.
- [ ] **Discover ports** via `tcpdump`/Wireshark on the capture host.
- [ ] **Capture traffic.** Run the logging stub on those ports; drive the client and hex-dump what it sends.
- [ ] **Document the framing.** Message boundaries, headers, opcodes, endianness, string encoding → `docs/PROTOCOL.md`.
- [ ] **Decode the login handshake** end to end (the first thing a server must answer).
- [ ] _Cross-check (optional):_ copy the installed client to the capture host and run `tools/client_inspect.py`.

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

Follow **[win98-bench.md](win98-bench.md)**:

1. Install the client on the Win98 box; point its DNS at the capture host's `dns_stub`.
2. Read off the hostnames, find the ports (`tcpdump`), and record them → `tools/redirect/hostnames.txt` + `PROTOCOL.md`.
3. Capture the **login handshake** with the logging stub and start documenting it in `docs/PROTOCOL.md`.
