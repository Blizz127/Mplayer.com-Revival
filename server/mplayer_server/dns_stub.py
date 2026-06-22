"""A logging/redirecting DNS stub for the Phase 1 capture bench.

Point a test machine's DNS resolver at the host running this, and it will:

  * **log every hostname** the original Mplayer client looks up (so you discover
    the client's endpoints without extracting files), and
  * **answer matching names with your capture server's IP**, transparently
    redirecting the client to the logging stub (``mplayer_server`` / the TCP/UDP
    listeners) — no HOSTS-file editing on the old box required.

Non-matching names can be forwarded to a real upstream resolver so the box stays
usable while you work.

Run (needs privileges to bind UDP/53)::

    sudo python -m mplayer_server.dns_stub --ip 192.168.1.50 \
        --match mplayer.com mpath.com --upstream 1.1.1.1

Then set the Win98 box's DNS server to 192.168.1.50. See docs/win98-bench.md.
"""

from __future__ import annotations

import argparse
import asyncio
import socket
import struct

from .capture import Capture
from .config import DEFAULT_CAPTURE_DIR

__all__ = ["parse_question", "build_a_response", "build_nxdomain", "suffix_matcher", "DNSRedirector"]

TYPE_A = 1
TYPE_ANY = 255


def parse_question(data: bytes) -> tuple[str, int, int]:
    """Parse the first question of a DNS query. Returns (qname, qtype, qclass).

    Assumes a standard query with the question name stored as uncompressed
    labels (true for real-world queries).
    """
    if len(data) < 12:
        raise ValueError("short DNS packet")
    pos = 12
    labels: list[str] = []
    while True:
        if pos >= len(data):
            raise ValueError("truncated name")
        length = data[pos]
        if length == 0:
            pos += 1
            break
        if length & 0xC0:  # compression pointer — not expected in a question
            raise ValueError("unexpected compression in question")
        pos += 1
        labels.append(data[pos : pos + length].decode("latin1"))
        pos += length
    qtype, qclass = struct.unpack_from(">HH", data, pos)
    return ".".join(labels), qtype, qclass


def _header_with_flags(query: bytes, flags: int, ancount: int) -> bytes:
    txn_id = query[:2]
    qdcount = struct.unpack_from(">H", query, 4)[0]
    return txn_id + struct.pack(">HHHHH", flags, qdcount, ancount, 0, 0)


def _question_bytes(query: bytes) -> bytes:
    # Everything from offset 12 to the end of the question section.
    pos = 12
    while data_len := query[pos]:
        pos += 1 + data_len
    pos += 1  # the zero-length root label
    pos += 4  # qtype + qclass
    return query[12:pos]


def build_a_response(query: bytes, ip: str, ttl: int = 60) -> bytes:
    """Build an answer mapping the queried name to ``ip`` (an A record)."""
    header = _header_with_flags(query, 0x8180, ancount=1)  # QR, RD, RA
    question = _question_bytes(query)
    answer = (
        b"\xc0\x0c"                      # name -> pointer to question at offset 12
        + struct.pack(">HHI", TYPE_A, 1, ttl)
        + struct.pack(">H", 4)          # rdlength
        + socket.inet_aton(ip)
    )
    return header + question + answer


def build_nxdomain(query: bytes) -> bytes:
    header = _header_with_flags(query, 0x8183, ancount=0)  # QR, RD, RA, RCODE=3
    return header + _question_bytes(query)


def suffix_matcher(suffixes: list[str]):
    """Return a predicate matching a qname against any of ``suffixes``."""
    norm = [s.lower().strip(".") for s in suffixes]

    def match(qname: str) -> bool:
        q = qname.lower().strip(".")
        return any(q == s or q.endswith("." + s) for s in norm)

    return match


class DNSRedirector(asyncio.DatagramProtocol):
    def __init__(self, ip, match, capture, *, answer_all=False, upstream=None):
        self.ip = ip
        self.match = match
        self.capture = capture
        self.answer_all = answer_all
        self.upstream = upstream
        self.transport: asyncio.DatagramTransport | None = None

    def connection_made(self, transport):
        self.transport = transport

    def datagram_received(self, data: bytes, addr):
        peer = f"{addr[0]}:{addr[1]}"
        try:
            qname, qtype, _ = parse_question(data)
        except ValueError:
            return
        self.capture.event("dns", peer, f"query {qname} (type {qtype})")

        if (self.answer_all or self.match(qname)) and qtype in (TYPE_A, TYPE_ANY):
            self.transport.sendto(build_a_response(data, self.ip), addr)
            self.capture.event("dns", peer, f">> A {qname} = {self.ip}  [REDIRECT]")
        elif self.upstream:
            asyncio.ensure_future(self._forward(data, addr))
        else:
            self.transport.sendto(build_nxdomain(data), addr)

    async def _forward(self, data: bytes, addr):
        try:
            loop = asyncio.get_running_loop()
            fut: asyncio.Future = loop.create_future()

            class _Up(asyncio.DatagramProtocol):
                def datagram_received(self, resp, _a):
                    if not fut.done():
                        fut.set_result(resp)

            transport, _ = await loop.create_datagram_endpoint(_Up, remote_addr=(self.upstream, 53))
            try:
                transport.sendto(data)
                resp = await asyncio.wait_for(fut, timeout=3.0)
                self.transport.sendto(resp, addr)
            finally:
                transport.close()
        except (asyncio.TimeoutError, OSError):
            self.transport.sendto(build_nxdomain(data), addr)


async def _serve(args) -> int:
    capture = Capture(args.capture_dir, also_stdout=not args.quiet)
    match = suffix_matcher(args.match)
    loop = asyncio.get_running_loop()
    transport, _ = await loop.create_datagram_endpoint(
        lambda: DNSRedirector(args.ip, match, capture, answer_all=args.all, upstream=args.upstream),
        local_addr=(args.host, args.port),
    )
    mode = "ALL names" if args.all else f"names under: {', '.join(args.match)}"
    print(f"DNS redirector on {args.host}:{args.port}  ->  {args.ip}")
    print(f"  redirecting: {mode}")
    print(f"  upstream for the rest: {args.upstream or '(none — NXDOMAIN)'}")
    print(f"  captures -> {capture.session_path}\nPress Ctrl+C to stop.")
    try:
        await asyncio.Event().wait()
    finally:
        transport.close()
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="mplayer_server.dns_stub", description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--ip", required=True, help="IP to answer matched names with (your capture server)")
    ap.add_argument("--match", nargs="*", default=["mplayer.com", "mpath.com"],
                    help="domain suffixes to redirect (default: mplayer.com mpath.com)")
    ap.add_argument("--all", action="store_true", help="redirect EVERY name to --ip (capture-all mode)")
    ap.add_argument("--upstream", help="forward non-matched queries to this resolver (e.g. 1.1.1.1)")
    ap.add_argument("--host", default="0.0.0.0", help="bind address (default: 0.0.0.0)")
    ap.add_argument("--port", type=int, default=53, help="bind port (default: 53; needs privileges)")
    ap.add_argument("--capture-dir", default=DEFAULT_CAPTURE_DIR)
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)
    try:
        return asyncio.run(_serve(args))
    except KeyboardInterrupt:  # pragma: no cover
        return 0
    except PermissionError:  # pragma: no cover
        print(f"error: binding {args.host}:{args.port} needs privileges — try sudo, or --port 5353")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
