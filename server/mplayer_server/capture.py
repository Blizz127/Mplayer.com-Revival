"""Capture sink: records connection events and byte traffic for protocol RE.

Every observed byte from the original client is written to a timestamped session
log (and optionally echoed to stdout) as a hexdump, so the raw material for
``docs/PROTOCOL.md`` is preserved exactly as it arrived.
"""

from __future__ import annotations

import datetime as _dt
import threading
from pathlib import Path

from .hexdump import hexdump

__all__ = ["Capture"]


def _timestamp() -> str:
    return _dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]


class Capture:
    """Thread/loop-safe writer for capture sessions.

    Parameters
    ----------
    directory:
        Where session logs are written. Created if missing.
    also_stdout:
        Echo every line to stdout as well (handy while driving the client live).
    """

    def __init__(self, directory: str | Path = "captures", *, also_stdout: bool = True) -> None:
        self.directory = Path(directory)
        self.directory.mkdir(parents=True, exist_ok=True)
        self.also_stdout = also_stdout
        self._lock = threading.Lock()
        session = _dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        self.session_path = self.directory / f"session-{session}.log"

    def _emit(self, line: str) -> None:
        with self._lock:
            with self.session_path.open("a", encoding="utf-8") as fh:
                fh.write(line + "\n")
            if self.also_stdout:
                print(line, flush=True)

    def event(self, binding: str, peer: str, message: str) -> None:
        """Record a non-data event (connect, disconnect, listen, error)."""
        self._emit(f"[{_timestamp()}] [{binding}] {peer} -- {message}")

    def data(self, binding: str, peer: str, direction: str, payload: bytes) -> None:
        """Record a chunk of bytes with a hexdump.

        ``direction`` is a short tag such as ``C->S`` (client to server).
        """
        header = f"[{_timestamp()}] [{binding}] {peer} {direction} {len(payload)} bytes"
        self._emit(header + "\n" + hexdump(payload))
