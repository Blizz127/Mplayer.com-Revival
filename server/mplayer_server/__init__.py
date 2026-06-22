"""Mplayer.com revival — server reimplementation.

Currently this package provides the Phase 1 reverse-engineering toolkit: a
logging stub server that captures what the original client sends. The auth,
lobby, matchmaking, and voice servers are added in later phases (see
``docs/ROADMAP.md``).
"""

from __future__ import annotations

__version__ = "0.0.1"

from .capture import Capture
from .hexdump import hexdump
from .logging_stub import Binding, LoggingStub

__all__ = ["Capture", "hexdump", "Binding", "LoggingStub", "__version__"]
