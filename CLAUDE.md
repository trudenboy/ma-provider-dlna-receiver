# CLAUDE.md — Development guide for DLNA Receiver provider

## Project overview

MA plugin provider that exposes Music Assistant as a UPnP/DLNA MediaRenderer.
External apps send audio via standard DLNA protocol; MA routes it to any player.

## Architecture

- **provider.py** — `DLNAReceiverProvider(PluginProvider)` with `AUDIO_SOURCE` feature
- **renderer.py** — `UPnPRenderer` aiohttp server handling SOAP actions
- **ssdp.py** — `SSDPAdvertiser` for multicast SSDP alive/byebye/search
- **constants.py** — UPnP URNs, config keys, MIME types

## Key flows

1. **Discovery**: SSDP advertises MediaRenderer → control point finds it
2. **SetAVTransportURI**: CP sends stream URL → stored in renderer state
3. **Play**: Provider creates `PluginSource`, calls `play_plugin_source()` on target
4. **Audio proxy**: `get_audio_stream()` fetches URL via aiohttp, yields chunks to MA pipeline

## Build & test

```bash
scripts/setup.sh          # One-time dev setup
source .venv/bin/activate
pytest                     # Run tests
ruff check provider/       # Lint
ruff format provider/      # Format
```

## Docker dev

```bash
docker compose -f docker-compose.dev.yml up
```

## CI

Uses `ma-provider-tools` wrapper workflows (ruff + mypy via trudenboy/ma-server fork).

## Important notes

- `network_mode: host` required in Docker for SSDP multicast
- UPnP eventing (SUBSCRIBE/NOTIFY) is NOT yet implemented — some control points
  may show stale transport state
- The SCPD XMLs are minimal stubs; full state variable tables would improve
  compatibility with strict control points
- `async-upnp-client` is in MA deps but we don't use it directly — we implement
  the *server* side, not the client side
