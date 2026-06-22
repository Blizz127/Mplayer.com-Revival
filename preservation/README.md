# Preservation

Original Mplayer.com software, archived for historical preservation and interoperability research. These are the
**ground-truth artifacts** the entire revival is built against.

## Contents

| Path | Description |
| --- | --- |
| `client/MplayerInstaller.exe` | The original Mplayer client installer (16-bit self-extracting setup). |
| `client/MplayerInstaller.exe.sha256` | Checksum sidecar for integrity verification. |

Verify integrity:

```bash
cd preservation/client && sha256sum -c MplayerInstaller.exe.sha256
```

See [../docs/installer-analysis.md](../docs/installer-analysis.md) for what static analysis reveals about this file.

## ⚠️ Legal

These binaries are **third-party proprietary software** (Mpath Interactive → HearMe → GameSpy/IGN lineage),
preserved here as **abandonware** for historical and interoperability purposes. They are **not** covered by the
project's GPL license and remain the property of their respective rights holders. If you are a rights holder and
want something removed, please open an issue.

Do not add binaries here unless they are necessary for preservation/interoperability and you can state their
provenance.

## Storage: Git LFS (intended)

These binaries should live in **Git LFS** rather than as normal git objects. `git-lfs` was not available in the
environment that created this commit, so `MplayerInstaller.exe` (~1.2 MB) is currently stored as a regular git
object — fine at this size, but LFS is preferred as the archive grows.

To migrate once `git lfs` is installed:

```bash
git lfs install
git lfs track "*.exe" "*.dll" "*.cab" "*.bin"      # writes ../.gitattributes
git lfs migrate import --include="*.exe,*.dll,*.cab,*.bin" --everything
git push --force-with-lease
```

After migrating, uncomment the LFS lines in the repo-root `.gitattributes`.
