---
title: Known Issues
---

# Known Issues

## The renderer is not discovered by a DLNA app

**Symptoms:** BubbleUPnP, mconnect, foobar2000 or another control point does not
list the Music Assistant renderer, even though the provider is loaded.

**Cause:** SSDP uses multicast on `239.255.255.250:1900`. Discovery does not
cross Docker bridge networking, VLANs, guest Wi-Fi isolation or a firewall that
blocks UDP 1900. The provider also needs a concrete IPv4 interface; IPv6-only
hosts are not supported.

**Fix:** Run Music Assistant with `network_mode: host`, put the control point
and Music Assistant on the same L2 network, allow UDP 1900 and the HTTP port
range (`8298+`), and configure `bind_ip` explicitly on multi-homed hosts.

---

## Several renderers cannot start on one host

**Symptoms:** The first player works, but adding a second player fails with an
SSDP bind error.

**Cause:** Every renderer joins the same SSDP multicast group and needs to share
UDP port 1900. The provider enables `SO_REUSEPORT` for that, which is not
available on every platform.

**Fix:** Use a platform with `SO_REUSEPORT` support (Linux), or expose a single
connected player per Music Assistant instance.

---

## A player has no renderer

**Symptoms:** A player is not listed in the Music Assistant renderer list.

**Cause:** Only playback-capable players (`player`, `stereo_pair`, `group`) are
eligible. Display, light, visualizer and source clients are intentionally
excluded. If **Connected players** is non-empty, only those players are used.

**Fix:** Select the player under **Settings → Plugins → DLNA Receiver →
Connected players**, or clear the selection to expose every eligible player.

---

## Sender Pause returns an error

**Symptoms:** The sender app shows an error when Pause is pressed, or playback
continues.

**Cause:** The bound output player does not support `PAUSE`. A DLNA sender can
only pause through the player, not by pausing the incoming live stream.

**Fix:** Pause on the sender when the target player supports pause; otherwise use
Stop. Music Assistant intentionally does not offer Pause on the live source.

---

## Renderers appear as extra Music Assistant players

**Symptoms:** With the DLNA **player** provider enabled, the virtual renderers
are discovered as additional Music Assistant players.

**Cause:** The upstream DLNA player provider does not yet skip devices whose
manufacturer is “Music Assistant” and model is “DLNA Receiver”. The receiver
already filters those players out of its own target list, so they cannot create
a feedback loop, but they still appear in the player list.

**Fix:** Do not select those virtual players as renderer targets. The upstream
DLNA provider change is tracked separately; it will hide them from discovery.

---

## A stream URL is rejected

**Symptoms:** `SetAVTransportURI` returns UPnP error 716 and playback does not
start.

**Cause:** Incoming URLs are restricted to `http`/`https` and must resolve to a
non-loopback, non-link-local, non-multicast destination. LAN addresses such as
`192.168.x.x` are allowed. Redirects are followed manually and re-validated.

**Fix:** Use a stream URL reachable from the Music Assistant host. Local-only
URLs such as `http://127.0.0.1/...` are rejected on purpose.

---

## “DLNA Stream” is shown without metadata

**Symptoms:** Playback works, but the Music Assistant UI shows a generic title
and no artwork.

**Cause:** The sender did not attach DIDL-Lite metadata to
`SetAVTransportURI`, or the metadata uses fields the provider does not map.

**Fix:** Use a sender that supplies DIDL-Lite title/artist/album/artwork. The
provider accepts `dc:title`, `upnp:artist`, `upnp:album`, `upnp:albumArtURI`
and `res@duration`.
