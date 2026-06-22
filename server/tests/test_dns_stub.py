import socket
import struct

from mplayer_server import dns_stub


def make_query(name: str, qtype: int = 1, txn: int = 0x1234) -> bytes:
    header = struct.pack(">HHHHHH", txn, 0x0100, 1, 0, 0, 0)  # RD set, 1 question
    q = b"".join(bytes([len(lbl)]) + lbl.encode("ascii") for lbl in name.split(".")) + b"\x00"
    q += struct.pack(">HH", qtype, 1)  # qtype, qclass=IN
    return header + q


def test_parse_question_roundtrip():
    qname, qtype, qclass = dns_stub.parse_question(make_query("www.mplayer.com"))
    assert qname == "www.mplayer.com"
    assert qtype == 1
    assert qclass == 1


def test_parse_question_rejects_short_packet():
    import pytest

    with pytest.raises(ValueError):
        dns_stub.parse_question(b"\x00\x01")


def test_build_a_response_points_to_ip():
    query = make_query("pop.mpath.com", txn=0xABCD)
    resp = dns_stub.build_a_response(query, "192.168.1.50", ttl=60)

    assert resp[:2] == query[:2]                       # transaction id preserved
    flags = struct.unpack_from(">H", resp, 2)[0]
    assert flags & 0x8000                              # QR (response) bit set
    assert struct.unpack_from(">H", resp, 6)[0] == 1   # ANCOUNT == 1
    assert b"\xc0\x0c" in resp                          # compression pointer to question
    assert resp.endswith(socket.inet_aton("192.168.1.50"))


def test_build_nxdomain_sets_rcode3():
    resp = dns_stub.build_nxdomain(make_query("example.org"))
    flags = struct.unpack_from(">H", resp, 2)[0]
    assert flags & 0x000F == 3                          # RCODE = NXDOMAIN
    assert struct.unpack_from(">H", resp, 6)[0] == 0    # no answers


def test_suffix_matcher():
    m = dns_stub.suffix_matcher(["mplayer.com", "mpath.com"])
    assert m("www.mplayer.com")
    assert m("mplayer.com")
    assert m("POP.MPATH.COM")          # case-insensitive
    assert not m("notmplayer.com")     # must match on a label boundary
    assert not m("mplayer.com.evil.net")
    assert not m("example.org")
