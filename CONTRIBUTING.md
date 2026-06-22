# Contributing

Thanks for helping revive Mplayer.com! A few ground rules keep this project healthy and legally clean.

## Clean-room reverse engineering

The reimplemented servers and protocol docs must be derived **only from observed behavior** — packet captures, and
disassembly/analysis of the preserved client we are interoperating with. Specifically:

- ✅ Do document what the client sends/expects, with hex evidence, in `docs/PROTOCOL.md`.
- ✅ Do write servers from those observations.
- ❌ Do **not** use leaked or proprietary Mpath/GameSpy **source code**, internal docs, or anything obtained under
  NDA.
- ❌ Do **not** copy code from other projects without a compatible license and attribution.

We are interoperating with abandoned software for preservation. Keep contributions on that footing.

## Protocol work

1. Capture with the logging stub (`server/`) while driving the original client.
2. Save raw captures under `server/captures/` and reference them from `docs/PROTOCOL.md`.
3. Document framing/messages with hex examples before implementing a server for them.

## Code

- **Server:** Python 3.11+, standard library first; justify any new dependency. Run `python -m pytest` in `server/`.
- Keep changes focused and matched to the surrounding style.
- Update the relevant `docs/` and tick the matching box in `docs/ROADMAP.md` when a milestone lands.

## Preservation binaries

Don't add third-party binaries unless necessary for preservation/interoperability, and always state provenance.
See `preservation/README.md`.
