#!/usr/bin/env python3
"""Serve the Mplayer.com Revival landing/status page.

A thin wrapper over the standard-library HTTP server, serving ``web/public/``.
No dependencies.

Usage::

    python web/serve.py                 # http://127.0.0.1:8000
    python web/serve.py --port 9000 --host 0.0.0.0
"""

from __future__ import annotations

import argparse
import functools
import http.server
import pathlib
import socketserver

PUBLIC = pathlib.Path(__file__).resolve().parent / "public"


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8000)
    args = ap.parse_args(argv)

    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(PUBLIC))
    with socketserver.TCPServer((args.host, args.port), handler) as httpd:
        print(f"Mplayer.com Revival — serving {PUBLIC}")
        print(f"  http://{args.host}:{args.port}/   (Ctrl+C to stop)")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nbye")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
