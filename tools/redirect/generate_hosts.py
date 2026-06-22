#!/usr/bin/env python3
"""Generate ``hosts``-file entries that point the original Mplayer client's
hardcoded hostnames at our revival server.

This is the faithful-track redirection mechanism (see ``docs/ARCHITECTURE.md``):
instead of patching the client binary, we override DNS for its hostnames so it
connects to us. Reads hostnames from ``hostnames.txt`` (one per line, ``#``
comments) and prints ready-to-paste ``hosts`` lines.

Usage::

    python generate_hosts.py                 # -> 127.0.0.1 for every hostname
    python generate_hosts.py --ip 192.168.1.50
    python generate_hosts.py --file hostnames.txt --ip 10.0.0.2

Then paste the output into:
  * Windows: C:\\Windows\\System32\\drivers\\etc\\hosts   (as Administrator)
  * macOS/Linux: /etc/hosts                               (with sudo)

Stdlib only.
"""

from __future__ import annotations

import argparse
import pathlib
import sys

MARKER = "# --- Mplayer.com Revival redirection ---"


def read_hostnames(path: pathlib.Path) -> list[str]:
    hosts: list[str] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.split("#", 1)[0].strip()
        if line:
            hosts.append(line)
    return hosts


def render(hostnames: list[str], ip: str) -> str:
    lines = [MARKER]
    lines += [f"{ip}\t{h}" for h in hostnames]
    lines.append("# --- end Mplayer.com Revival ---")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--file",
        type=pathlib.Path,
        default=pathlib.Path(__file__).with_name("hostnames.txt"),
        help="hostname list (default: hostnames.txt next to this script)",
    )
    parser.add_argument("--ip", default="127.0.0.1", help="target IP (default: 127.0.0.1)")
    args = parser.parse_args(argv)

    if not args.file.exists():
        print(f"error: {args.file} not found", file=sys.stderr)
        return 1

    hostnames = read_hostnames(args.file)
    if not hostnames:
        print(
            f"No hostnames in {args.file} yet.\n"
            "Phase 1 task: extract the client's hardcoded hostnames and add them there\n"
            "(see docs/ROADMAP.md and docs/installer-analysis.md).",
            file=sys.stderr,
        )
        return 2

    print(render(hostnames, args.ip))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
