"""Tests for the logging stub.

Async bodies are driven with ``asyncio.run`` so the suite needs only ``pytest``
itself — no ``pytest-asyncio`` plugin.
"""

import asyncio

import pytest

from mplayer_server import Binding, Capture, LoggingStub


async def _drive_tcp(capture):
    async with LoggingStub([Binding("tcp", 0, "test")], capture, host="127.0.0.1") as stub:
        port = stub.ports["test"]
        assert port > 0
        reader, writer = await asyncio.open_connection("127.0.0.1", port)
        writer.write(b"MZ\x00hello")
        await writer.drain()
        writer.close()
        await asyncio.sleep(0.05)  # let the server read + log


def test_tcp_capture_records_client_bytes(tmp_path):
    capture = Capture(tmp_path, also_stdout=False)
    asyncio.run(_drive_tcp(capture))

    log = capture.session_path.read_text()
    assert "TCP connect" in log
    assert "C->S 8 bytes" in log
    assert "4d 5a 00" in log  # "MZ\x00"
    assert "|MZ.hello|" in log
    assert "TCP disconnect" in log


async def _drive_udp(capture):
    async with LoggingStub([Binding("udp", 0, "voice")], capture, host="127.0.0.1") as stub:
        port = stub.ports["voice"]
        loop = asyncio.get_running_loop()
        transport, _ = await loop.create_datagram_endpoint(
            asyncio.DatagramProtocol, remote_addr=("127.0.0.1", port)
        )
        transport.sendto(b"\x01\x02\x03\x04")
        await asyncio.sleep(0.05)
        transport.close()


def test_udp_capture_records_datagram(tmp_path):
    capture = Capture(tmp_path, also_stdout=False)
    asyncio.run(_drive_udp(capture))

    log = capture.session_path.read_text()
    assert "C->S 4 bytes" in log
    assert "01 02 03 04" in log


def test_binding_rejects_bad_proto():
    with pytest.raises(ValueError):
        Binding("sctp", 1234)


def test_ports_assigned_for_each_binding(tmp_path):
    async def _check():
        capture = Capture(tmp_path, also_stdout=False)
        async with LoggingStub(
            [Binding("tcp", 0, "a"), Binding("udp", 0, "b")], capture, host="127.0.0.1"
        ) as stub:
            assert set(stub.ports) == {"a", "b"}
            assert all(p > 0 for p in stub.ports.values())

    asyncio.run(_check())
