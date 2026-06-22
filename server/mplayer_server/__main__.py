"""Command-line entry point for the logging stub.

Examples
--------
Listen on a couple of TCP ports and one UDP port, logging everything::

    python -m mplayer_server --tcp 7000 7777 --udp 6500

Then redirect the original client's hostnames to this machine (see
``tools/redirect/``) and drive it; captures appear under ``--capture-dir``.
"""

from __future__ import annotations

import argparse
import asyncio

from . import __version__
from .capture import Capture
from .config import DEFAULT_BINDINGS, DEFAULT_CAPTURE_DIR
from .logging_stub import Binding, LoggingStub


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="mplayer_server",
        description="Mplayer revival logging stub — capture what the original client sends.",
    )
    p.add_argument("--tcp", nargs="*", type=int, default=[], metavar="PORT", help="TCP ports to listen on")
    p.add_argument("--udp", nargs="*", type=int, default=[], metavar="PORT", help="UDP ports to listen on")
    p.add_argument("--host", default="0.0.0.0", help="Address to bind (default: 0.0.0.0)")
    p.add_argument(
        "--capture-dir",
        default=DEFAULT_CAPTURE_DIR,
        help=f"Directory for capture logs (default: {DEFAULT_CAPTURE_DIR})",
    )
    p.add_argument("--quiet", action="store_true", help="Do not echo captures to stdout")
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    return p.parse_args(argv)


def _build_bindings(args: argparse.Namespace) -> list[Binding]:
    bindings = [Binding("tcp", port, f"tcp/{port}") for port in args.tcp]
    bindings += [Binding("udp", port, f"udp/{port}") for port in args.udp]
    return bindings or list(DEFAULT_BINDINGS)


async def _run(args: argparse.Namespace) -> int:
    bindings = _build_bindings(args)
    if not bindings:
        print(
            "No ports to listen on. Pass --tcp/--udp ports, or seed DEFAULT_BINDINGS "
            "in config.py once Phase 1 discovers them.\n"
            "Example: python -m mplayer_server --tcp 7000 --udp 6500"
        )
        return 2

    capture = Capture(args.capture_dir, also_stdout=not args.quiet)
    stub = LoggingStub(bindings, capture, host=args.host)
    await stub.start()

    print(f"mplayer_server {__version__} — logging stub")
    for label, port in stub.ports.items():
        print(f"  listening {label:<12} on {args.host}:{port}")
    print(f"Captures -> {capture.session_path}\nPress Ctrl+C to stop.")

    try:
        await stub.serve_forever()
    except (KeyboardInterrupt, asyncio.CancelledError):  # pragma: no cover
        pass
    finally:
        await stub.stop()
    return 0


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        return asyncio.run(_run(args))
    except KeyboardInterrupt:  # pragma: no cover
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
