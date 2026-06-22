# The Windows 98 capture bench (Phase 1)

A period Windows 98 box is the ideal test bench — it runs the original 16-bit installer and the Mplayer client
natively, exactly like the TEN and GameSpy revivals do. This guide takes you from a blank Win98 box to a captured
login handshake.

The trick: **don't run anything on Win98 except the client.** Modern Python won't run there, so all our tooling
(the DNS redirector, the logging stub, packet capture) runs on a second machine — the **capture host** — on the
same LAN. We steer the client to us with DNS.

```
   ┌────────────────────┐         LAN          ┌──────────────────────────────┐
   │  Windows 98 box     │  ◄──────────────►   │  Capture host                 │
   │  · Mplayer client    │   + static route    │  LAN IP 192.168.1.50          │
   │  · DNS = 100.111... │   to 100.64.0.0/10  │  Tailscale 100.111.220.11     │
   │  · 192.168.1.40     │                     │  · dns_stub / logging stub    │
   └────────────────────┘                     │  · tcpdump · client_inspect   │
                                                └──────────────────────────────┘
```

## Prerequisites

- **Win98 box**: TCP/IP bound to a working NIC; ideally a **static IP** (e.g. `192.168.1.40`).
- **Capture host**: this repo + Python 3.11+ + Tailscale, on the same LAN as the Win98 box. It has two addresses —
  its **LAN IP** (e.g. `192.168.1.50`) and a stable **Tailscale IP** (`100.111.220.11`) that never changes.
- The preserved installer: `preservation/client/MplayerInstaller.exe`.
- An **isolated/trusted LAN**. The DNS redirector answers authoritatively for whatever you point at it.

> Throughout, `100.111.220.11` is the capture/server host's **Tailscale IP** (the stable address the client targets),
> `192.168.1.50` is that same host's **LAN IP** (used only as the route gateway), and `192.168.1.40` is the Win98 box.

## Using your Tailscale IP (100.111.220.11)

Tailscale gives the capture host a stable address that survives IP changes — ideal as the *canonical* server address
baked into the client's config. **But Tailscale's client needs Windows 10+, so the Win98 box can't join the tailnet
itself.** Instead, give Win98 a one-line static route so it reaches the Tailscale IP *through* the capture host on
the LAN:

```text
REM On the Win98 box (DOS prompt). 100.64.0.0/10 is Tailscale's range; gateway = capture host's LAN IP.
C:\> route add 100.64.0.0 mask 255.192.0.0 192.168.1.50
```

Now `100.111.220.11` is reachable from Win98. Use it as the DNS server and the redirect target everywhere below.

- **Bind our servers to this IP** (`--host 100.111.220.11`, as shown below). This matters for UDP/DNS: a `0.0.0.0`
  bind would let the kernel answer *from* the LAN IP (`192.168.1.50`, the egress interface), and the client — which
  queried `100.111.220.11` — would reject the mismatched reply. Binding to the IP makes replies come from it.
- Win98 9x doesn't persist routes across reboots — add that `route add` line to `C:\AUTOEXEC.BAT`.
- This works because `100.111.220.11` is a *local* address on the capture host; no IP-forwarding needed to reach the
  host itself. (To reach *other* tailnet nodes you'd also enable IP forwarding and a Tailscale subnet route.)
- **Prefer the simple path?** If you don't want the route, just use the capture host's **LAN IP** (`192.168.1.50`)
  for everything below instead of the Tailscale IP — fine for a same-LAN bench; you only lose the swap-proof address.

---

## Step 1 — Install the client on Win98

Get the installer onto the Win98 box (CD-R, a FAT32 USB stick with Win98 USB drivers, or a LAN share) and run it.
It's a 16-bit self-extractor that unpacks to `%TEMP%` and installs normally on Win98. Note the install directory
(commonly `C:\Program Files\Mplayer` or similar).

## Step 2 — Start the DNS redirector on the capture host

This logs every hostname the client looks up **and** points the matched ones at your capture host. Start in
**capture-all** mode for the first run so nothing is missed, forwarding everything else upstream so the box stays
usable:

```bash
cd server
sudo python -m mplayer_server.dns_stub --host 100.111.220.11 --ip 100.111.220.11 --all --upstream 1.1.1.1
# (UDP/53 needs privileges. Prefer matched mode once you know the domains:)
# sudo python -m mplayer_server.dns_stub --host 100.111.220.11 --ip 100.111.220.11 --match mplayer.com mpath.com --upstream 1.1.1.1
```

Open the capture host firewall for **UDP/53** (and later the stub ports).

## Step 3 — Point Win98 at our DNS

On the Win98 box: **Control Panel → Network → TCP/IP → [your NIC] → Properties → DNS Configuration**:

1. Enable DNS.
2. Under **DNS Server Search Order**, add `100.111.220.11` and move it to the top (remove others for a clean capture).
3. OK out and **reboot** (Win98's resolver picks up DNS changes on reboot; there is no `ipconfig /flushdns`).

## Step 4 — Launch the client and read off the hostnames

Start the Mplayer client and try to log in. Watch the `dns_stub` console — every lookup is logged, e.g.:

```
[dns] 192.168.1.40 query www.mplayer.com (type 1)
[dns] 192.168.1.40 >> A www.mplayer.com = 100.111.220.11  [REDIRECT]
[dns] 192.168.1.40 query pop.mplayer.com (type 1)
...
```

Record every Mplayer/Mpath hostname you see into [`../tools/redirect/hostnames.txt`](../tools/redirect/hostnames.txt)
and the endpoints table in [`PROTOCOL.md`](PROTOCOL.md). Switch `dns_stub` to `--match` mode now that you know them.

## Step 5 — Discover the ports (packet capture)

DNS sent the client to your capture host, but on *what ports*? See the connection attempts directly:

```bash
# on the capture host, while launching/logging in on Win98:
sudo tcpdump -n -i any "host 192.168.1.40 and (tcp[tcpflags] & tcp-syn != 0 or udp)"
```

Each line shows `192.168.1.40 -> 100.111.220.11.<PORT>` — those destination ports are the Mplayer services. Record
them next to their hostnames in `PROTOCOL.md`.

## Step 6 — Capture the actual bytes (the login handshake)

Now run the **logging stub** on the discovered ports so the client's connection lands somewhere that hex-dumps it:

```bash
cd server
python -m mplayer_server --host 100.111.220.11 --tcp <PORT1> <PORT2> --udp <PORT3>
```

Relaunch the client. The stub records the first thing the client sends — the **login handshake** — as a hexdump
under `server/captures/`. This is the raw material for the auth server.

> Tip: keep `tcpdump`/Wireshark running alongside the stub. The stub sees TCP payloads cleanly; a packet capture is
> the backstop for UDP and for anything the stub's port list missed.

## Step 7 — Document and implement

1. Reference the capture file from [`PROTOCOL.md`](PROTOCOL.md) and document the framing (length prefixes? opcodes?
   ASCII vs binary? endianness?).
2. Decode the login exchange first — it's the first thing a server must answer.
3. We then implement the **auth server** to satisfy that handshake, and iterate (lobby → matchmaking).

---

## Getting the installed client off the box (optional, powerful)

Copying the installed files to the capture host lets [`client_inspect.py`](../tools/client_inspect.py) pull
hostnames/ports/strings statically — a great cross-check against the live capture. Win98 has a built-in FTP client:

```text
C:\> cd "C:\Program Files\Mplayer"
C:\> ftp 192.168.1.50          (log into an FTP server on the capture host)
ftp> binary
ftp> mput *.*
```

Then on the capture host:

```bash
python tools/client_inspect.py ./uploaded-client --hostnames-out tools/redirect/hostnames.txt
```

(USB stick with Win98 drivers, a CD-R, or a LAN share also work. Or just zip the folder and hand it to me.)

## Alternative: HOSTS-file redirect (instead of DNS)

If you'd rather not change DNS, edit `C:\WINDOWS\HOSTS` (no extension; copy `hosts.sam` as a template) and add the
known hostnames — generate the lines with:

```bash
python tools/redirect/generate_hosts.py --ip 100.111.220.11
```

DNS is recommended for **discovery** (it reveals hostnames you don't know yet); HOSTS is fine once the list is fixed.

## Win98 gotchas

- **No `ipconfig`** — use `winipcfg` (GUI) for IP info; **reboot** to apply DNS changes / clear the resolver.
- **Tailscale IP unreachable?** Confirm the static route (`route print`) and that the gateway is the capture host's
  LAN IP; the route is lost on reboot unless it's in `AUTOEXEC.BAT`. Or fall back to the LAN IP.
- Give the box a **static IP** so `tcpdump` filters and firewall rules stay stable.
- **Capture-host firewall**: allow inbound **UDP/53** and the stub's TCP/UDP ports from the Win98 IP.
- If the client uses an **IP literal** (not a hostname), DNS/HOSTS can't catch it — the packet capture will reveal
  that, and we fall back to a small client patch (documented if we hit it).
- Keep it on an **isolated LAN**; the DNS redirector is authoritative for whatever you aim it at.
