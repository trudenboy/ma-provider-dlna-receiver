---
title: Configuration
---

# Configuration

## Adding DLNA Receiver to Music Assistant

1. Open **Music Assistant → Settings → Plugins**.
2. Click **Add Provider** and select **DLNA Receiver**.
3. Pick one or more **Connected players** and save.
4. Open a DLNA control point on the same network and select the advertised
   renderer.

No account or authentication is required: the provider is a local UPnP
MediaRenderer and accepts streams from the LAN.

## Settings

| Setting | Description | Default |
|:--------|:------------|:--------|
| **Friendly name** | Prefix for the advertised renderer names, e.g. `Music Assistant — Kitchen` | `Music Assistant` |
| **Connected players** | Playback-capable players that get a renderer. Empty means every eligible player. | *(empty)* |
| **Bind IP** | IPv4 address for the UPnP HTTP servers and SSDP. Must be a concrete address, not `0.0.0.0` or loopback. | auto-detected |
| **HTTP port** | Base port for the UPnP HTTP servers. Multiple renderers increment it (`8298`, `8299`, …). | `8298` |

Only `player`, `stereo_pair` and `group` clients are offered in **Connected
players**. Display, light, visualizer and source clients cannot render audio and
are excluded.

> **Upgrading from 1.2.x:** the old `target_players` selection is not migrated.
> Re-select the players under **Connected players** after upgrading to 1.3.0.

## Network requirements

- Music Assistant must expose a concrete IPv4 address. IPv6-only hosts are not
  supported by SSDP/UPnP discovery here.
- Docker must use `network_mode: host`; bridge networking does not pass SSDP
  multicast.
- Allow UDP `1900` and TCP ports `8298+` between the control point and Music
  Assistant.
- Multiple renderers share SSDP port `1900` via `SO_REUSEPORT`; use a platform
  that supports it (Linux).

## How players are exposed

With an empty **Connected players** list, every eligible Music Assistant player
gets its own renderer. Control points see them individually:

- *Music Assistant — Kitchen*
- *Music Assistant — Living Room*
- *Music Assistant — Yandex Station*

Each renderer has a stable UDN derived from the player ID, so bookmarks in
BubbleUPnP / mconnect survive restarts and provider reloads.
