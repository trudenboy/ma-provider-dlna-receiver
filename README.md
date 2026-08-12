# DLNA Receiver — Music Assistant Plugin Provider


<!-- >>> ma-provider-tools sync (readme header) — DO NOT EDIT >>> -->
[![CI](https://github.com/trudenboy/ma-provider-dlna-receiver/actions/workflows/test.yml/badge.svg)](https://github.com/trudenboy/ma-provider-dlna-receiver/actions/workflows/test.yml)
[![Release](https://img.shields.io/github/v/release/trudenboy/ma-provider-dlna-receiver?display_name=tag)](https://github.com/trudenboy/ma-provider-dlna-receiver/releases/latest)
[![License](https://img.shields.io/github/license/trudenboy/ma-provider-dlna-receiver)](LICENSE)
[![Music Assistant](https://img.shields.io/badge/Music%20Assistant-9070B8?logo=python&logoColor=white)](https://www.music-assistant.io/)[![stable](https://img.shields.io/endpoint?url=https%3A%2F%2Ftrudenboy.github.io%2Fma-provider-tools%2Fbadges%2Fdlna_receiver-stable.json)](https://github.com/music-assistant/server/releases/latest)[![beta](https://img.shields.io/endpoint?url=https%3A%2F%2Ftrudenboy.github.io%2Fma-provider-tools%2Fbadges%2Fdlna_receiver-beta.json)](https://github.com/music-assistant/server/releases?q=prerelease)
[![Stars](https://img.shields.io/github/stars/trudenboy/ma-provider-dlna-receiver?style=flat&logo=github)](https://github.com/trudenboy/ma-provider-dlna-receiver/stargazers)

**📖 [Documentation](https://trudenboy.github.io/ma-provider-dlna-receiver/)** · **🔄 [Changelog](CHANGELOG.md)** · **🐛 [Issues](https://github.com/trudenboy/ma-provider-dlna-receiver/issues)** · **💬 [Discussions](https://github.com/trudenboy/ma-provider-dlna-receiver/discussions)**
<!-- <<< ma-provider-tools sync (readme header) <<< -->

Expose Music Assistant as a **UPnP/DLNA MediaRenderer** on the local network.

External apps (Qobuz, BubbleUPnP, foobar2000, mconnect, Kodi, etc.) discover
the virtual renderer via SSDP, send audio streams, and MA routes them to any
configured player — DLNA devices, AirPlay speakers, Chromecast, Yandex Station,
and more.

## How it works

```
┌──────────────┐   SSDP discover   ┌──────────────────────┐
│  Qobuz /     │ ◄──────────────── │  MA DLNA Receiver    │
│  BubbleUPnP  │                   │  (UPnP MediaRenderer)│
│              │  SetAVTransportURI │                      │
│              │ ──────────────────►│  renderer.py         │
│              │  Play / Pause      │  ssdp.py             │
│              │ ──────────────────►│  provider.py         │
└──────────────┘                   └──────────┬───────────┘
                                              │ PluginSource
                                              ▼
                                   ┌──────────────────────┐
                                   │  MA Streaming Engine  │
                                   │  (decode → DSP →     │
                                   │   encode → HTTP)     │
                                   └──────────┬───────────┘
                                              │
                                              ▼
                                   ┌──────────────────────┐
                                   │  Target Player       │
                                   │  (DLNA / AirPlay /   │
                                   │   Cast / Station)    │
                                   └──────────────────────┘
```

## Multi-player mode

By default, the **Target players** selection is empty, which dynamically exposes
**every eligible MA player** as a separate DLNA renderer on your network. Use
the multi-select setting to expose only specific players. Control points see
them individually:

- *Music Assistant — Kitchen*
- *Music Assistant — Living Room*
- *Music Assistant — Yandex Station*

Each renderer has a stable UDN (UUID5 derived from player ID) so bookmarks
in BubbleUPnP / mconnect persist across restarts.

## Quick start

### Docker (recommended)

```bash
docker compose -f docker-compose.dev.yml up
```

### Local development

```bash
scripts/setup.sh
source .venv/bin/activate
```

## Configuration

| Key | Description | Default |
|-----|-------------|---------|
| `friendly_name` | Prefix for DLNA renderer names | `Music Assistant` |
| `target_players` | Player multi-select; empty exposes all eligible players | *(empty)* |
| `bind_ip` | IP for UPnP HTTP server & SSDP | *(auto-detect)* |
| `http_port` | Base port for UPnP HTTP servers | `8298` |

> In multi-player mode ports auto-increment: 8298, 8299, 8300, …

## Project structure

```
provider/
  __init__.py      — setup(), get_config_entries()
  provider.py      — DLNAReceiverProvider + RendererInstance
  renderer.py      — UPnP MediaRenderer HTTP server + SOAP + GENA eventing
  eventing.py      — GENA subscription manager (SUBSCRIBE/NOTIFY)
  ssdp.py          — SSDP advertisement and M-SEARCH responder
  constants.py     — UPnP URNs, config keys, defaults
  manifest.json    — MA provider metadata
  scpd/            — Full UPnP service description XMLs
    AVTransport.xml
    RenderingControl.xml
    ConnectionManager.xml
tests/
scripts/
  setup.sh         — local dev environment setup
  docker-init.sh   — Docker container init script
```

## UPnP compliance

- **AVTransport**: SetAVTransportURI, Play, Pause, Stop, Seek, GetTransportInfo, GetPositionInfo, GetMediaInfo
- **RenderingControl**: GetVolume, SetVolume, GetMute, SetMute
- **ConnectionManager**: GetProtocolInfo, GetCurrentConnectionIDs, GetCurrentConnectionInfo
- **GENA Eventing**: SUBSCRIBE/UNSUBSCRIBE/NOTIFY with LastChange events
- **SSDP**: alive/byebye/M-SEARCH response for all service types

## Status

🧪 **Experimental** — under active development.

## License

Apache-2.0
