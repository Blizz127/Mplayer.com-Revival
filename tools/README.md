# Tools

Helper utilities for the revival.

| Tool | Purpose |
| --- | --- |
| [`client_inspect.py`](client_inspect.py) | Scan extracted client binaries for network indicators — hostnames (flagging mplayer.com/mpath.com), URLs, IP literals, likely ports, DLL refs, Winsock usage. Reads ASCII **and** UTF-16LE strings. Can emit a `hostnames.txt` for `redirect/`. |
| [`redirect/`](redirect/) | Point the original Mplayer client at our servers by overriding its hardcoded hostnames (via the system `hosts` file). The faithful-track equivalent of OpenSpy's DNS redirection — no binary patching. |

```bash
# Phase 1: after extracting the client on Windows/otvdm —
python tools/client_inspect.py /path/to/extracted/client --hostnames-out tools/redirect/hostnames.txt
```

More tools will land as phases progress (e.g. an IPX-over-UDP tunnel helper).
