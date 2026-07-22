# Changelog

## [1.2.3] - 2026-07-22

### Fixed

- Empty target-player configuration now exposes all available Music Assistant players and no longer advertises an unplayable unbound renderer while no players are registered.
- DLNA `Play` now resumes paused playback without reopening the upstream stream or resetting elapsed time, and duplicate `Play` commands no longer restart an already-playing track.

## [1.2.1] - 2026-07-09

### Fixed

- Code style compliance with the stricter upstream Music Assistant lint configuration (no functional changes).

## [1.2.0] - 2026-07-09

### Changed

- Migrated to the new Music Assistant plugin sources architecture: each virtual DLNA renderer is now exposed as a first-class audio source and playback from a DLNA sender starts through the standard play flow.
- Pausing the incoming DLNA stream from the Music Assistant UI is no longer offered (matching other receiver providers); pause from the sender app instead.
- Configuration entry labels and descriptions are now localizable instead of hardcoded English text.

### Fixed

- Elapsed time and stream metadata are now tracked per renderer, so simultaneous casts to different renderers no longer corrupt each other's progress display.
- Stopping playback from the Music Assistant side now stops the renderer's progress tracking instead of leaving it running in the background.
- A renderer without an active cast now reports a clear error when playback is attempted, instead of playing silence.
- Taking over an exclusive DLNA source from another player now stops the previous player first.
- The fallback renderer (no target players configured) is startable again from the Live Inputs view.

## [1.1.8] - 2026-05-09

### Changed

- Rewrote 7 Google-style docstrings (`provider/eventing.py::EventingManager.subscribe/.renew/.notify`, `provider/provider.py::DLNAReceiverProvider._on_set_transport_uri`) to Sphinx-style `:param:` / `:returns:` / `:raises:` per the upstream music-assistant/server CLAUDE.md docstring rule.

## 0.0.1 (unreleased)

- Initial project scaffold
- UPnP MediaRenderer with AVTransport, RenderingControl, ConnectionManager
- SSDP advertisement and M-SEARCH response
- PluginProvider integration with MA streaming pipeline
- Docker and local dev environment setup
