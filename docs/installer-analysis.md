# Installer Analysis

Static analysis of the preserved installer, `preservation/client/MplayerInstaller.exe`. This is what we know
*without* running it; extracting and running it is a Phase 1 task (needs a 16-bit-capable Windows environment).

## Identity & checksums

| Field | Value |
| --- | --- |
| Archived as | `preservation/client/MplayerInstaller.exe` |
| Size | 1,226,922 bytes (~1.2 MB) |
| SHA-256 | `ec8a0d4deb01c3f3e43742204b38752398d1d2fc624a2a6d5bbb5f8331b96450` |
| MD5 | `9b8c996a0f7f457ba93cff7ad4a0fc85` |
| Format | MS-DOS / **NE (New Executable)**, "for MS Windows 3.x (3.10)" — i.e. **16-bit Windows** |

(Checksum sidecar: `preservation/client/MplayerInstaller.exe.sha256`.)

## What the header tells us

Parsing the NE header:

- **It's a self-extracting installer stub.** Internal module name **`GLBSSTUB`** with a single export
  `___EXPORTEDSTUB`; the non-resident name is **`STUB.exe`**. Linked with the **Borland linker 5.60**.
- **Imports** only the core Win16 DLLs: `KERNEL`, `USER`, `GDI` (plus its own `STUB` self-reference) — consistent
  with a thin extractor stub rather than the application itself.
- **The real payload is appended and compressed.** Beyond the stub, the file is ~1.2 MB of packed data. A
  whole-file string scan surfaces no readable hostnames, DLL names, or URLs — only the stub's own `STUB.exe`. The
  client binaries and their hardcoded server names live **inside the compressed payload** and aren't visible until
  the payload is decompressed.
- **Embedded installer graphics** are detectable: a GIF (≈ offset `0x109414`) and several BMPs (the setup
  wizard art / Mplayer branding).

## Implications

1. **Win11 caveat:** a 16-bit NE binary **cannot run on 64-bit Windows 11** (no NTVDM/WOW16). To extract it we need a
   32-bit Windows VM or a 16-bit shim like [otvdm/winevdm](https://github.com/otya128/winevdm). See
   [client-modernization.md](client-modernization.md).
2. **Static RE has hit its limit here.** The hostnames/ports/protocol can't be read from the packed installer. The
   path forward is dynamic: **extract → install → inspect the installed client** (32-bit?) and **capture its
   traffic**.

## Next steps (Phase 1)

- [ ] Run the installer under a 16-bit-capable Windows environment and capture the **list of installed files**.
- [ ] Identify the main client EXE/DLLs and whether they are 16-bit or 32-bit (decides the Win11 compat story).
- [ ] Extract hardcoded hostnames/ports and INI/registry config → `tools/redirect/hostnames.txt`, `PROTOCOL.md`.
- [ ] Salvage the branding art (GIF/BMPs) — useful reference for the modernized client and web frontend.

## Reproducing this analysis

The header/signature scan was done with a short Python script (stdlib only): parse the MZ→NE header, read the
resident/non-resident name tables and imported-names table, then scan the whole file for archive/compression and
image signatures (`MSCF`, `SZDD`, `PK\x03\x04`, `GIF8`, `BM`, …). No third-party tools required.
