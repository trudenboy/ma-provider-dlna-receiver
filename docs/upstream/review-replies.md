# Draft replies for upstream review threads

These are drafts only. A human maintainer must read, adjust and post them.
Do not paste them without checking the final diff.

## 1. Volume and mute always report 50 / off

Addressed in v1.3.0: `GetVolume`, `GetMute` and the initial RenderingControl
event now read `volume_level` / `volume_muted` from the bound player. A
`PLAYER_UPDATED` event mirrors later changes into the renderer and notifies GENA
subscribers, so a sender no longer jumps from 15 to ~52 on the first volume step.

## 2. Use the player-bound plugin model

Addressed in v1.3.0: the provider now exposes `connected_players` through
`create_connected_players_entry()`, implements
`get_player_audio_sources(player_id)`, and only creates renderers for
`PLAYBACK_TARGET_TYPES`. Display, light, visualizer and source clients are
excluded, and a restricted user only sees sources for players they can access.

This is a config change: the 1.2.x `target_players` value is not migrated, as
agreed for the 1.3.0 release; users reselect players once.

## 3. Stop/Pause/resume after ownership was lost

Addressed in v1.3.0: Stop, Pause and pause-resume now check the active claim
before touching the player. A late sender command is rejected with UPnP 701
instead of stopping unrelated playback, and a failed player command returns a
SOAP fault rather than being swallowed.

## 4. `audio/L16` is advertised but cannot be probed

Addressed in v1.3.0: `audio/L16` was removed from the advertised sink protocol
list. The stream stays `ContentType.UNKNOWN` so ffmpeg probes the actual codec
for the compressed formats senders commonly use.

## 5. LastChange namespaces

Addressed in v1.3.0: LastChange now uses
`urn:schemas-upnp-org:metadata-1-0/AVT/` for AVTransport and
`urn:schemas-upnp-org:metadata-1-0/RCS/` for RenderingControl. A regression
test asserts both namespaces.

## 6. SCPD is read synchronously on the event loop

Addressed in v1.3.0: the three SCPD files are loaded once at module import into
`SCPD_CACHE`; renderer construction and requests no longer touch the filesystem.

## 7. The `dlna` player provider discovers these virtual renderers

The receiver already filters its own UDNs out of the target list, so there is no
feedback loop. Hiding the virtual devices from the `dlna` **player** provider is
a change in a different provider, so it is prepared as a separate upstream
change in `docs/upstream/dlna-player-skip.md` rather than growing this PR's
provider scope. Please confirm whether you prefer that separate change or a
same-PR modification to `music_assistant/providers/dlna/player.py`.
