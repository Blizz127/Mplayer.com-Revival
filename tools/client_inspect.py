#!/usr/bin/env python3
"""Inspect extracted Mplayer client binaries for network indicators.

Once the original installer is run on Windows (or otvdm/a VM) and the client is
extracted, point this at the install directory. It scans every file for ASCII
*and* UTF-16LE strings (Windows apps store plenty of wide strings) and reports
the network indicators that matter for Phase 1:

  * hostnames (highlighting mplayer.com / mpath.com)
  * URLs and raw IPv4 literals
  * likely ports
  * referenced DLLs/EXEs and Winsock usage

It can also emit a ``hostnames.txt`` ready for ``tools/redirect/``.

Usage::

    python client_inspect.py /path/to/extracted/client
    python client_inspect.py MPLAYER.EXE --hostnames-out found.txt
    python client_inspect.py ./client --json report.json

Stdlib only.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import defaultdict

ASCII_RUN = re.compile(rb"[\x20-\x7e]{4,}")
WIDE_RUN = re.compile(rb"(?:[\x20-\x7e]\x00){4,}")

HOSTNAME = re.compile(
    r"\b(?:[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+"
    r"(?:com|net|org|gov|edu|mil|int|info|biz|tv|cc|io|us|local)\b",
    re.IGNORECASE,
)
URL = re.compile(r"(?:https?|ftp|rtsp)://[^\s\"'<>]+", re.IGNORECASE)
IPV4 = re.compile(r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b")
PORT = re.compile(r"(?:port|socket|listen|connect)\D{0,6}(\d{2,5})", re.IGNORECASE)
DLLREF = re.compile(r"\b[A-Za-z0-9_]{2,32}\.(?:dll|exe|ocx|vxd)\b", re.IGNORECASE)
WINSOCK_HINTS = ("WSAStartup", "ws2_32", "wsock32", "winsock", "gethostbyname", "WSASocket", "recvfrom")

# Hostnames worth flagging loudly.
RELEVANT = ("mplayer", "mpath", "pop.", "hearme", "rogerwilco", "gamespy")


def iter_strings(data: bytes):
    """Yield decoded ASCII and UTF-16LE strings found in ``data``."""
    for m in ASCII_RUN.finditer(data):
        yield m.group().decode("latin1")
    for m in WIDE_RUN.finditer(data):
        try:
            yield m.group().decode("utf-16-le")
        except UnicodeDecodeError:  # pragma: no cover - defensive
            pass


def scan_bytes(data: bytes) -> dict[str, set[str]]:
    found: dict[str, set[str]] = defaultdict(set)
    for s in iter_strings(data):
        for h in HOSTNAME.findall(s):
            found["hostnames"].add(h.lower())
        for u in URL.findall(s):
            found["urls"].add(u)
        for ip in IPV4.findall(s):
            if ip not in ("0.0.0.0", "255.255.255.255", "127.0.0.1"):
                found["ips"].add(ip)
        for p in PORT.findall(s):
            found["ports"].add(p)
        for d in DLLREF.findall(s):
            found["dll_refs"].add(d.lower())
        if any(w.lower() in s.lower() for w in WINSOCK_HINTS):
            found["winsock"].add(s.strip()[:80])
    return found


def scan_file(path: pathlib.Path) -> dict[str, set[str]]:
    try:
        return scan_bytes(path.read_bytes())
    except OSError as e:  # pragma: no cover - defensive
        print(f"  ! cannot read {path}: {e}", file=sys.stderr)
        return {}


def merge(into: dict[str, set[str]], other: dict[str, set[str]]) -> None:
    for k, v in other.items():
        into.setdefault(k, set()).update(v)


def collect_files(root: pathlib.Path) -> list[pathlib.Path]:
    if root.is_file():
        return [root]
    return sorted(p for p in root.rglob("*") if p.is_file())


def format_report(agg: dict[str, set[str]]) -> str:
    lines: list[str] = []

    def section(title: str, key: str, highlight: tuple[str, ...] = ()) -> None:
        items = sorted(agg.get(key, set()))
        lines.append(f"\n## {title} ({len(items)})")
        if not items:
            lines.append("  (none)")
            return
        for it in items:
            star = "  <-- RELEVANT" if any(h in it.lower() for h in highlight) else ""
            lines.append(f"  {it}{star}")

    section("Hostnames", "hostnames", RELEVANT)
    section("URLs", "urls", RELEVANT)
    section("IPv4 literals", "ips")
    section("Likely ports", "ports")
    section("DLL / EXE references", "dll_refs")
    section("Winsock / networking hints", "winsock")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path", type=pathlib.Path, help="file or directory of extracted client files")
    ap.add_argument("--hostnames-out", type=pathlib.Path, help="write discovered hostnames (for tools/redirect/)")
    ap.add_argument("--json", type=pathlib.Path, help="write the full report as JSON")
    args = ap.parse_args(argv)

    if not args.path.exists():
        print(f"error: {args.path} does not exist", file=sys.stderr)
        return 1

    files = collect_files(args.path)
    print(f"Scanning {len(files)} file(s) under {args.path} ...")
    agg: dict[str, set[str]] = {}
    for f in files:
        merge(agg, scan_file(f))

    print(format_report(agg))

    if args.hostnames_out:
        hosts = sorted(agg.get("hostnames", set()))
        header = "# Hostnames discovered by client_inspect.py — review before using.\n"
        args.hostnames_out.write_text(header + "\n".join(hosts) + "\n", encoding="utf-8")
        print(f"\nWrote {len(hosts)} hostname(s) -> {args.hostnames_out}")

    if args.json:
        args.json.write_text(
            json.dumps({k: sorted(v) for k, v in agg.items()}, indent=2), encoding="utf-8"
        )
        print(f"Wrote JSON report -> {args.json}")

    relevant = [h for h in agg.get("hostnames", set()) if any(r in h for r in RELEVANT)]
    if relevant:
        print(f"\n>>> {len(relevant)} relevant hostname(s) found — add to tools/redirect/hostnames.txt + PROTOCOL.md")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
