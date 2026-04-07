# DLNA Receiver — Music Assistant Plugin Provider

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

Set `target_players` to `*` to expose **every MA player** as a separate DLNA
renderer on your network.  Control points see them individually:

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
| `target_players` | Comma-separated player IDs, or `*` for all | *(empty — single renderer)* |
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
