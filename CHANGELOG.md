# Changelog

## [1.2.5] - 2026-08-05

### Changed

- Renderer creation and cleanup now react immediately when Music Assistant players are added or removed.

### Fixed

- Provider options are now available on loaded instances with safe defaults and legacy target-player compatibility.
- Prevented receiver renderers from being selected recursively by matching their device UUID identifiers.
- DLNA control points now receive accurate Play failures, external stop notifications, and media duration.
- Oversized or malformed DIDL metadata is rejected safely, while unexpected task and eventing errors remain visible.

## [1.2.4] - 2026-07-29

### Fixed

- Prevented DLNA renderers discovered by Music Assistant from being selected as new receiver targets and creating a recursive renderer loop.
- Playback state now returns to stopped when Music Assistant ends a cast, while the current stream remains available for a subsequent Play command.
- Unsupported seek requests now return a standards-compliant SOAP error instead of an opaque server error.
- DLNA control points now receive current playback position and duration, ordered event notifications, and standards-compliant discovery responses.
- The provider now displays a cast-audio icon in the Music Assistant interface.

### Security

- Limited active event subscriptions and their lifetime to prevent unbounded memory and notification-task growth from devices on the local network.

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
