"""Tests for tools/client_inspect.py.

The tool is a standalone script, so we load it by path with importlib rather
than importing a package.
"""

import importlib.util
import pathlib

_TOOL = pathlib.Path(__file__).resolve().parents[2] / "tools" / "client_inspect.py"
_spec = importlib.util.spec_from_file_location("client_inspect", _TOOL)
client_inspect = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(client_inspect)


def _build_blob() -> bytes:
    # Real binaries NUL-separate and word-align their strings; join tokens with
    # NULs so ASCII runs don't bleed into each other (and a trailing ASCII char
    # can't be mistaken as the first byte of the following wide string).
    parts = [
        b"some binary junk",
        b"www.mplayer.com",                       # ASCII hostname (relevant)
        "chat.mpath.com".encode("utf-16-le"),     # wide hostname (relevant)
        b"http://register.mplayer.com/signup",     # URL
        b"connect to port 7000 now",               # port hint
        b"server 207.155.0.42 here",               # IPv4 literal
        b"WSOCK32.dll WSAStartup",                 # dll ref + winsock hint
    ]
    return b"\x00\x00\x00\x00".join(parts)


def test_finds_ascii_and_wide_hostnames():
    found = client_inspect.scan_bytes(_build_blob())
    assert "www.mplayer.com" in found["hostnames"]
    assert "chat.mpath.com" in found["hostnames"]  # proves UTF-16LE decoding works


def test_finds_url_ip_port_and_winsock():
    found = client_inspect.scan_bytes(_build_blob())
    assert any("register.mplayer.com" in u for u in found["urls"])
    assert "207.155.0.42" in found["ips"]
    assert "7000" in found["ports"]
    assert "wsock32.dll" in found["dll_refs"]
    assert found["winsock"]  # WSAStartup hint captured


def test_localhost_and_broadcast_ips_filtered():
    found = client_inspect.scan_bytes(b"127.0.0.1 and 0.0.0.0 and 255.255.255.255")
    assert not found.get("ips")


def test_report_flags_relevant_hostnames():
    agg = client_inspect.scan_bytes(_build_blob())
    report = client_inspect.format_report(agg)
    assert "RELEVANT" in report
    assert "## Hostnames" in report


def test_empty_input_is_clean():
    assert client_inspect.scan_bytes(b"") == {}
