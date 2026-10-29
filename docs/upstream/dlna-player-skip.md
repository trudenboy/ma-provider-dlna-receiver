# Upstream change: skip Music Assistant DLNA receivers in the `dlna` player provider

This change belongs to `music_assistant/providers/dlna/player.py`, not to the
DLNA Receiver provider. Apply it in a separate upstream PR, or explicitly ask
the maintainers to include it in `#3611`.

## Why

The DLNA Receiver advertises a MediaRenderer whose device description already
contains:

```xml
<manufacturer>Music Assistant</manufacturer>
<modelName>DLNA Receiver</modelName>
```

The `dlna` **player** provider discovers every MediaRenderer and registers it as
a Music Assistant player. That adds one redundant player per virtual renderer.
The receiver filters those UDNs out of its own target list, so there is no
feedback loop, but the player list is still cluttered.

## Proposed patch

```diff
--- a/music_assistant/providers/dlna/player.py
+++ b/music_assistant/providers/dlna/player.py
@@ -113,6 +113,16 @@ class DLNAPlayer(Player):
         """
         await self._device_connect()

+        if (
+            self.device
+            and (self.device.manufacturer or "").strip() == "Music Assistant"
+            and (self.device.model_name or "").strip() == "DLNA Receiver"
+        ):
+            self.logger.debug("Ignoring %s - Music Assistant DLNA receiver", self.device.name)
+            await self._device_disconnect()
+            self.mass.players.delete_player_config(self.player_id)
+            return False
+
         if self.device and not self.device.has_play_media:
             self.logger.debug("Ignoring %s - no play capability", self.device.name)
             return False
```

`setup()` already returns `False` for devices that must be ignored, and the
caller adds the UDN to `_ignored_udns`, so no player is registered and no
event subscription is left behind.

## Test plan

- Unit: a discovered DMR with manufacturer `Music Assistant` and model
  `DLNA Receiver` makes `setup()` return `False`.
- Unit: a normal DMR still registers.
- Manual: enable the `dlna` player provider and the DLNA Receiver provider.
  Confirm the virtual renderers are not added as players, while real DLNA
  speakers are still discovered.
- Regression: the receiver's own UDN filter still prevents selecting a virtual
  renderer as a target.

## Alternatives considered

- Filter in `on_upnp_service_discovered` before fetching the description. This
  avoids a connection but requires a second description fetch or duplicating
  the UPnP factory; `setup()` already owns device metadata and cleanup.
- Filter by UDN prefix. The UDN is a UUID5 derived from the player id, so it is
  stable but opaque; manufacturer/model is the protocol-visible contract.
