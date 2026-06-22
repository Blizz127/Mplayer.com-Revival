"""Classic ``hexdump``-style formatting for captured protocol bytes."""

from __future__ import annotations

__all__ = ["hexdump"]


def hexdump(data: bytes, width: int = 16) -> str:
    """Render ``data`` as an offset / hex / ASCII dump.

    Example::

        00000000  4d 5a 90 00 03 00 00 00  04 00 00 00 ff ff 00 00  |MZ..............|

    Bytes are grouped 8 + 8 per row (the traditional layout) and non-printable
    bytes render as ``.`` in the ASCII column.
    """
    if not data:
        return "  (no data)"

    rows: list[str] = []
    for offset in range(0, len(data), width):
        chunk = data[offset : offset + width]

        hex_cells = [f"{b:02x}" for b in chunk]
        # Pad so short final rows still align with full rows.
        hex_cells += ["  "] * (width - len(chunk))
        left = " ".join(hex_cells[: width // 2])
        right = " ".join(hex_cells[width // 2 :])

        ascii_col = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
        rows.append(f"{offset:08x}  {left}  {right}  |{ascii_col}|")

    return "\n".join(rows)
