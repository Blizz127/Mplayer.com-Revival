# Client tracks: Faithful & Modernized

We pursue **two clients in parallel**, both speaking the same reverse-engineered protocol (the shared contract from
`PROTOCOL.md`). One maximizes authenticity; the other maximizes longevity and reach (Windows 11 and beyond).

---

## Track A — Faithful (the original client)

Run the **original, preserved Mplayer client**, unmodified where possible, pointed at our reimplemented servers via
hostname redirection (`tools/redirect/`). This is the authenticity benchmark and how we validate that our servers
behave correctly.

### The Windows 11 problem (and the fix)

The preserved **installer is 16-bit** (NE / "Windows 3.x"; see [installer-analysis.md](installer-analysis.md)).
**64-bit Windows 11 cannot execute 16-bit code at all** — the old NTVDM/WOW16 layer doesn't exist on x64/ARM64. So:

| Component | Bitness | Runs on Win11 x64? | Mitigation |
| --- | --- | --- | --- |
| The installer | 16-bit (confirmed) | ❌ No | 32-bit Windows VM, or [otvdm/winevdm](https://github.com/otya128/winevdm) (a Win16 emulator for modern Windows) |
| The client itself | _likely 32-bit, **TBD** (Phase 1)_ | ✅ if 32-bit (WOW64) | Compatibility mode; shims for legacy display/DirectX/DirectPlay |

**Plan for Track A:**
1. **Phase 1:** extract the client in a 16-bit-capable environment and determine the client's bitness.
2. If the client is **32-bit**, it should run on Win11 x64 under WOW64 — wrap it in a **modern installer** (so users
   skip the 16-bit installer entirely) plus a compatibility shim/launcher that applies the right flags and points it
   at our servers.
3. Address era-specific breakage: legacy **DirectPlay**/DirectDraw, fixed-palette/low-res display, and any
   IP-literal/hostname assumptions.
4. If any *essential* component is 16-bit, ship **otvdm** as the supported way to run it, or reimplement that
   component for the modern client (Track B).

> Note: 64-bit Windows 11 still runs **32-bit** apps via WOW64, so a 32-bit client is the good case. Only 16-bit
> pieces are hard-blocked.

---

## Track B — Modernized (a new client)

A **new, cross-platform client** that re-creates the Mplayer experience (login, lobby, chat/emotes, matchmaking,
voice) and speaks the same protocol — so it works against the same servers as the original. This is the durable
answer to "runs on Windows 11 *etc.*": native on Win11, and on macOS/Linux too.

### Why build it

- **Longevity:** no dependency on decades-old 16/32-bit binaries or shims.
- **Reach:** "etc." — one codebase for Windows 11, macOS, Linux (and potentially the browser).
- **Maintainability:** modern UI toolkit, modern crypto/networking, fixes for issues the original never will get.

### Stack — _to decide when Track B starts (early Phase 4, or sooner once the protocol is stable)_

Candidates, to be chosen with the protocol shape and contributor skills in mind:

- **Web / Electron / Tauri** — fastest to a polished, recognizable UI; easy cross-platform; pairs naturally with the
  web frontend.
- **C#/.NET (Avalonia or WinUI)** — strong on Windows, good native feel, cross-platform via Avalonia.
- **Qt (C++/PySide)** — native performance; good for real-time voice and tight protocol/audio handling.

A faithful re-creation of the original look-and-feel (including the animated "gizmos") is an explicit goal; the
branding art salvaged from the installer (GIF/BMPs) is the visual reference.

---

## How the tracks relate

```
                 docs/PROTOCOL.md  (shared contract)
                ┌────────────┴────────────┐
        Track A: original client    Track B: new client
        (faithful, via redirect)    (modern, native Win11/mac/Linux)
                └────────────┬────────────┘
                     server/ (one set of servers)
```

Track A comes first because it **validates the servers against ground truth**. Track B can begin as soon as the
protocol is stable enough to implement against, and reuses every server we build for Track A.
