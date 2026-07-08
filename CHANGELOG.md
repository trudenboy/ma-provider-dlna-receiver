# Changelog

## [1.1.9] - 2026-07-08

### Changed

- Migrated to the new Music Assistant plugin sources architecture: each virtual DLNA renderer is now exposed as a first-class audio source (visible under "Live Inputs") and playback from a DLNA sender starts through the standard play flow.
- Configuration entry labels and descriptions are now localizable instead of hardcoded English text.

## [1.1.8] - 2026-05-09

### Changed

- Rewrote 7 Google-style docstrings (`provider/eventing.py::EventingManager.subscribe/.renew/.notify`, `provider/provider.py::DLNAReceiverProvider._on_set_transport_uri`) to Sphinx-style `:param:` / `:returns:` / `:raises:` per the upstream music-assistant/server CLAUDE.md docstring rule.

## 0.0.1 (unreleased)

- Initial project scaffold
- UPnP MediaRenderer with AVTransport, RenderingControl, ConnectionManager
- SSDP advertisement and M-SEARCH response
- PluginProvider integration with MA streaming pipeline
- Docker and local dev environment setup
