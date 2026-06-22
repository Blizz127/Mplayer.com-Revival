# Mplayer revival — server

Python reimplementation of the Mplayer.com servers. Right now it contains the **Phase 1 reverse-engineering
toolkit**: a logging stub that captures what the original client sends so we can document the protocol. Auth, lobby,
matchmaking, and voice servers come in later phases — see [../docs/ROADMAP.md](../docs/ROADMAP.md).

Runtime is **Python 3.11+ standard library only** (asyncio); no runtime dependencies.

## Run the logging stub

```bash
# From this directory. Listen on whatever TCP/UDP ports the client uses
# (placeholders below until Phase 1 discovers the real ones):
python -m mplayer_server --tcp 7000 7777 --udp 6500

# Options:
#   --host 0.0.0.0        address to bind
#   --capture-dir DIR     where logs go (default: ./captures, git-ignored)
#   --quiet               don't echo captures to stdout
```

It logs every byte the client sends as a hexdump and never replies — the point of Phase 1 is to *observe* the
client's opening moves. Point the original client here with [../tools/redirect/](../tools/redirect/).

A `mplayer-stub` console script is also installed if you `pip install -e .`.

## Develop & test

```bash
pip install -e ".[dev]"   # or just: pip install pytest
python -m pytest          # 8 tests, no pytest-asyncio plugin needed
```

`conftest.py` puts the package on the path so tests run from a fresh checkout without installing.

## Layout

```
mplayer_server/
  hexdump.py        classic offset/hex/ascii dump
  capture.py        Capture: timestamped session logs of events + byte traffic
  logging_stub.py   Binding + LoggingStub: asyncio TCP/UDP logging listeners
  config.py         registry of discovered hostnames/ports (filled during Phase 1)
  __main__.py       CLI entry point
tests/              unit + integration tests
```
