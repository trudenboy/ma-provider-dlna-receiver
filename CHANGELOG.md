# Changelog

## [1.1.8] - 2026-05-09

### Changed

- Rewrote 7 Google-style docstrings (`provider/eventing.py::EventingManager.subscribe/.renew/.notify`, `provider/provider.py::DLNAReceiverProvider._on_set_transport_uri`) to Sphinx-style `:param:` / `:returns:` / `:raises:` per the upstream music-assistant/server CLAUDE.md docstring rule.

## 0.0.1 (unreleased)

- Initial project scaffold
- UPnP MediaRenderer with AVTransport, RenderingControl, ConnectionManager
- SSDP advertisement and M-SEARCH response
- PluginProvider integration with MA streaming pipeline
- Docker and local dev environment setup
