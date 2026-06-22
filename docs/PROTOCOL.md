# Mplayer Protocol Notes

> **Status:** empty — to be filled during Phase 1 (reverse-engineering). This file is the authoritative record of
> the Mplayer wire protocol as we discover it. Everything here must come from **observed behavior** (captures,
> disassembly of the preserved client) — never from leaked source. See [../CONTRIBUTING.md](../CONTRIBUTING.md).

## How to add to this document

1. Capture traffic with the logging stub (`server/mplayer_server`) while driving the original client.
2. Save the raw capture under `server/captures/` and reference it here by filename.
3. Document the framing, then individual messages, with hex evidence.

---

## Endpoints

The hostnames/ports the client connects to. Mirror this table into `tools/redirect/hostnames.txt`.

| Hostname | Port | Proto | Purpose | Evidence |
| --- | --- | --- | --- | --- |
| _TODO_ | _?_ | _?_ | _?_ | _capture / strings_ |

## Framing

_How are messages delimited? Length-prefixed (size + body)? Newline-delimited text? Fixed headers?_
_Endianness? String encoding (ASCII/CP-1252)?_

- TODO

## Message catalog

Document each message as it's decoded. Suggested template:

```
### <NAME>  (direction: C->S | S->C)

Opcode / tag : 0x??
Layout       :
  offset  size  type     field            notes
  0       2     u16(le)  length           total incl. header?
  ...
Example (hex):
  00000000  ...                                  |....|
Server must : <what a correct server replies>
```

### Login handshake

_The first exchange a server must satisfy. Highest priority — decode this first._

- TODO

## Open questions

- Game connection model per title: IPX-over-UDP tunnel vs. brokered direct IP? (Phase 3)
- Is voice a separate server/port? Codec? (Phase 4)
- Any encryption/obfuscation on the control streams?
