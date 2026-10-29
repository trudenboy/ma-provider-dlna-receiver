# What does this implement/fix?

New **plugin provider** that exposes Music Assistant as a UPnP/DLNA MediaRenderer
on the local network. External apps (BubbleUPnP, Qobuz, foobar2000, mconnect,
Kodi, etc.) discover MA via SSDP and cast audio streams to any connected player.

Built on the **plugin sources architecture** (#3938): each virtual renderer is a
first-class `AudioSource` media item, playback starts through the standard
`play_media` flow, and exclusive stream ownership is managed via
`on_source_selected` / `on_source_unselected` with the stream-session-id guard.

### Key features

- **SSDP discovery** — advertises virtual MediaRenderers via multicast
  (`239.255.255.250:1900`)
- **Player-bound sources** — `connected_players` selects playback-capable
  players; each player only sees the `AudioSource` bound to it
- **Multi-player mode** — one renderer per connected player (e.g.
  "Music Assistant — Kitchen"), each with a unique UDN and HTTP port
- **DIDL-Lite metadata** — title, artist, album, cover art and duration
- **Volume and mute sync** — RenderingControl reads the bound player's real
  state and `PLAYER_UPDATED` events push changes to GENA subscribers
- **Ownership guards** — late Stop/Pause from a sender cannot affect playback
  owned by another source
- **Audio proxy** — the incoming stream URL is fetched server-side
  (`StreamType.CUSTOM`) with SSRF/redirect guards; `ContentType.UNKNOWN` lets
  ffmpeg probe arbitrary compressed input
- **GENA eventing** — subscriptions for `AVTransport`, `RenderingControl` and
  `ConnectionManager`, with standard `metadata-1-0/AVT` and `metadata-1-0/RCS`
  namespaces
- **Recursion filter** — own renderers are excluded from the player list
- **Full SCPD** — complete service description XMLs, cached once per process

### Architecture

```
DLNA Control Point
       │
       ▼
  SSDP Discovery ──► UPnP HTTP Server (SOAP actions)
                           │
                           ▼
                  AudioSource (plugin sources)
                           │
                           ▼
                  MA streaming pipeline ──► Target Player
```

### Changed files

| File | Description |
|------|-------------|
| `__init__.py` | Provider setup |
| `provider.py` | `DLNAReceiverProvider(PluginProvider)` — lifecycle, connected-player sources, ownership, metadata, audio proxy |
| `renderer.py` | `UPnPRenderer` — aiohttp server, SOAP actions, GENA, volume/mute sync |
| `ssdp.py` | `SSDPAdvertiser` — multicast SSDP alive/byebye/search responses |
| `eventing.py` | GENA subscription manager (SUBSCRIBE/RENEW/UNSUBSCRIBE/NOTIFY) |
| `constants.py` | UPnP URNs, config keys, MIME types |
| `strings.json` | Localizable config entry labels/descriptions |
| `scpd/*.xml` | Full service description XMLs |
| `manifest.json` | Provider manifest (`plugin`, domain `dlna_receiver`) |
| `tests/` | 206 unit tests covering the plugin-sources contract, renderer, SSDP and eventing |

### Notes

- Requires `network_mode: host` in Docker for SSDP multicast
- Pausing the live source from the MA UI is intentionally not offered
  (`can_play_pause=False`); pause happens in the sender app via SOAP
- The `target_players` option from 1.2.x is replaced by Music Assistant's
  `connected_players`; users re-select players once after upgrading
- The upstream `dlna` **player** provider still discovers these virtual
  renderers as players. A separate one-provider change will skip devices whose
  manufacturer is "Music Assistant" and model is "DLNA Receiver"; the receiver
  already excludes them from its own target list, so there is no feedback loop.

**Related issue (if applicable):**

- Documentation PR: music-assistant/music-assistant.io#626
- Plugin sources architecture: #3938

> **Source**: [trudenboy/ma-provider-dlna-receiver](https://github.com/trudenboy/ma-provider-dlna-receiver) · tag [v1.3.0](https://github.com/trudenboy/ma-provider-dlna-receiver/releases/tag/v1.3.0)

## Types of changes

- [ ] Bugfix (non-breaking change which fixes an issue) — `bugfix`
- [ ] New feature (non-breaking change which adds functionality) — `new-feature`
- [ ] Enhancement to an existing feature — `enhancement`
- [x] New music/player/metadata/plugin provider — `new-provider`
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected) — `breaking-change`
- [ ] Refactor (no behaviour change) — `refactor`
- [ ] Documentation only — `documentation`
- [ ] Maintenance / chore — `maintenance`
- [ ] CI / workflow change — `ci`
- [ ] Dependencies bump — `dependencies`

## Checklist

- [x] The code change is tested and works locally.
- [x] `pre-commit run --all-files` passes.
- [x] `pytest` passes, and tests have been added/updated under `tests/` where applicable.
- [ ] For changes to shared models, the companion PR in `music-assistant/models` is linked.
- [ ] For changes affecting the UI, the companion PR in `music-assistant/frontend` is linked.
- [x] I have read and complied with the project's [AI Policy](https://github.com/music-assistant/.github/blob/main/AI_POLICY.md) for any AI-assisted contributions.
- [x] I have raised a PR against the documentation repository targeting the main or beta branch as appropriate.
