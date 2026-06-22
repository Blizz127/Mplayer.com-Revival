from mplayer_server.hexdump import hexdump


def test_empty():
    assert hexdump(b"") == "  (no data)"


def test_offset_hex_and_ascii_columns():
    out = hexdump(b"MZ\x90\x00")
    assert out.startswith("00000000  ")
    assert "4d 5a 90 00" in out
    # Printable chars shown; the NUL becomes a dot.
    assert out.endswith("|MZ..|")


def test_multiple_rows_have_increasing_offsets():
    out = hexdump(bytes(range(20)))  # 20 bytes -> two rows of 16
    lines = out.splitlines()
    assert len(lines) == 2
    assert lines[0].startswith("00000000  ")
    assert lines[1].startswith("00000010  ")


def test_non_printable_rendered_as_dots():
    out = hexdump(b"\x00\x01\x7f\xff")
    assert out.endswith("|....|")
