"""A logging stub server — the first reverse-engineering tool.

It listens on the TCP/UDP ports the original Mplayer client tries to reach and
records every byte the client sends (via :class:`Capture`). It deliberately does
*not* reply: the goal of Phase 1 is to observe what the client says first, so we
can document the protocol before implementing real servers.

Bind a port to ``0`` to get an OS-assigned ephemeral port (used by the tests);
the actual port chosen is reported back in :attr:`LoggingStub.ports`.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass

from .capture import Capture

__all__ = ["Binding", "LoggingStub"]


@dataclass(frozen=True)
class Binding:
    """A single port to listen on."""

    proto: str  # "tcp" or "udp"
    port: int
    name: str = ""

    def __post_init__(self) -> None:
        if self.proto not in ("tcp", "udp"):
            raise ValueError(f"proto must be 'tcp' or 'udp', got {self.proto!r}")

    @property
    def label(self) -> str:
        return self.name or f"{self.proto}/{self.port}"


def _peer(addr: object) -> str:
    if isinstance(addr, tuple) and len(addr) >= 2:
        return f"{addr[0]}:{addr[1]}"
    return str(addr)


class _UDPProtocol(asyncio.DatagramProtocol):
    def __init__(self, capture: Capture, label: str) -> None:
        self._capture = capture
        self._label = label

    def datagram_received(self, data: bytes, addr: object) -> None:
        self._capture.data(self._label, _peer(addr), "C->S", data)


class LoggingStub:
    """Run a set of TCP/UDP logging listeners.

    Usable as an async context manager::

        async with LoggingStub(bindings, capture) as stub:
            print(stub.ports)
            await stub.serve_forever()
    """

    def __init__(
        self,
        bindings: list[Binding],
        capture: Capture,
        host: str = "0.0.0.0",
    ) -> None:
        self.bindings = bindings
        self.capture = capture
        self.host = host
        self.ports: dict[str, int] = {}
        self._servers: list[asyncio.AbstractServer] = []
        self._transports: list[asyncio.BaseTransport] = []

    async def _handle_tcp(
        self,
        label: str,
        reader: asyncio.StreamReader,
        writer: asyncio.StreamWriter,
    ) -> None:
        peer = _peer(writer.get_extra_info("peername"))
        self.capture.event(label, peer, "TCP connect")
        try:
            while True:
                data = await reader.read(65536)
                if not data:
                    break
                self.capture.data(label, peer, "C->S", data)
        except (ConnectionResetError, asyncio.IncompleteReadError, OSError):
            pass
        finally:
            self.capture.event(label, peer, "TCP disconnect")
            writer.close()

    async def start(self) -> dict[str, int]:
        """Bind all listeners. Returns ``{label: actual_port}``."""
        loop = asyncio.get_running_loop()
        for b in self.bindings:
            label = b.label
            if b.proto == "tcp":

                def _cb(reader, writer, _label=label):
                    return asyncio.ensure_future(self._handle_tcp(_label, reader, writer))

                server = await asyncio.start_server(_cb, self.host, b.port)
                port = server.sockets[0].getsockname()[1]
                self._servers.append(server)
            else:  # udp
                transport, _ = await loop.create_datagram_endpoint(
                    lambda c=self.capture, n=label: _UDPProtocol(c, n),
                    local_addr=(self.host, b.port),
                )
                port = transport.get_extra_info("sockname")[1]
                self._transports.append(transport)

            self.ports[label] = port
            self.capture.event(label, "-", f"listening {b.proto} {self.host}:{port}")
        return self.ports

    async def serve_forever(self) -> None:
        await asyncio.Event().wait()  # until cancelled

    async def stop(self) -> None:
        for server in self._servers:
            server.close()
        for server in self._servers:
            try:
                await server.wait_closed()
            except Exception:  # pragma: no cover - best-effort shutdown
                pass
        for transport in self._transports:
            transport.close()
        self._servers.clear()
        self._transports.clear()

    async def __aenter__(self) -> "LoggingStub":
        await self.start()
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self.stop()
