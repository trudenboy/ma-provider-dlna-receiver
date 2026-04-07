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
| `friendly_name` | Name visible to DLNA control points | `Music Assistant` |
| `target_player` | MA player ID to route audio to | *(empty — select at runtime)* |
| `bind_ip` | IP for UPnP HTTP server & SSDP | *(auto-detect)* |
| `http_port` | Port for UPnP HTTP server | `8298` |

## Project structure

```
provider/
  __init__.py      — setup(), get_config_entries()
  provider.py      — DLNAReceiverProvider (PluginProvider)
  renderer.py      — UPnP MediaRenderer HTTP server + SOAP handlers
  ssdp.py          — SSDP advertisement and M-SEARCH responder
  constants.py     — UPnP URNs, config keys, defaults
  manifest.json    — MA provider metadata
tests/
scripts/
  setup.sh         — local dev environment setup
  docker-init.sh   — Docker container init script
```

## Status

🧪 **Experimental** — under active development.

## License

Apache-2.0
