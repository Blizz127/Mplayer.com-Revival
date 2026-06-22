# Hostname redirection

The faithful track runs the **original, unmodified** Mplayer client and simply makes its hardcoded server hostnames
resolve to *our* server. This is the same approach OpenSpy uses for GameSpy titles — no binary patching.

## Workflow

1. **Discover** the hostnames the client uses (Phase 1) and list them in [`hostnames.txt`](hostnames.txt),
   one per line. (Also mirror them into `docs/PROTOCOL.md`.)
2. **Generate** `hosts`-file entries pointing them at your server:

   ```bash
   python generate_hosts.py --ip 127.0.0.1
   ```

3. **Apply** by pasting the output into your system `hosts` file:
   - **Windows:** `C:\Windows\System32\drivers\etc\hosts` (edit as Administrator)
   - **macOS/Linux:** `/etc/hosts` (use `sudo`)

4. Start the server (`server/`), launch the client, and watch it connect to you.

## Notes

- `hostnames.txt` has no real entries yet — they're filled in during Phase 1 (see
  [../../docs/ROADMAP.md](../../docs/ROADMAP.md)).
- A `hosts` file can only redirect **hostnames**. If the client has a raw **IP literal** baked in, redirection won't
  catch it and we fall back to a targeted binary patch (documented when/if we hit that case).
- For a fuller setup (multiple machines, or clients that bypass `hosts`), run a small DNS server and point the test
  machine at it — same idea, just network-wide. The `hosts` method is the simplest per-machine option.
