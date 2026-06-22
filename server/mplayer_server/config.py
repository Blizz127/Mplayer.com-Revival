"""Configuration and the running registry of reverse-engineering discoveries.

As Phase 1 progresses, fill in the hostnames and ports the original client uses.
Keep this in sync with ``tools/redirect/hostnames.txt`` and ``docs/PROTOCOL.md``.
"""

from __future__ import annotations

from .logging_stub import Binding

# Where captures are written by default.
DEFAULT_CAPTURE_DIR = "captures"

# Hostnames the original client is known to contact. EMPTY until Phase 1 extracts
# them from the client binary/INI. Record discoveries here (and in
# tools/redirect/hostnames.txt) as: "hostname"  # purpose, evidence
KNOWN_HOSTNAMES: list[str] = [
    # "www.mplayer.com",   # web frontend (guess — confirm in Phase 1)
    # "pop.mpath.com",     # POP/lobby server (guess — confirm in Phase 1)
]

# Ports to listen on with the logging stub. UNKNOWN until Phase 1 — override on
# the command line (e.g. `python -m mplayer_server --tcp 7000 --udp 6500`).
# Seed this list once real ports are discovered from the client.
DEFAULT_BINDINGS: list[Binding] = [
    # Binding("tcp", 7000, "lobby?"),   # placeholder — confirm in Phase 1
]
