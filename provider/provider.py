"""DLNA Receiver — Main provider implementation.

Registers as a PluginProvider with AUDIO_SOURCE feature so that audio
received from external DLNA control points is routed through the MA
streaming pipeline to any configured player.
"""

from __future__ import annotations

import asyncio
import logging
import socket
from typing import TYPE_CHECKING, Any

from music_assistant.models import PluginProvider, ProviderFeature
from music_assistant_models.config_entries import ConfigValueType
from music_assistant_models.enums import ContentType, MediaType
from music_assistant_models.media_items import AudioFormat
from music_assistant_models.plugin import PluginSource

from .constants import (
    CONF_BIND_IP,
    CONF_FRIENDLY_NAME,
    CONF_HTTP_PORT,
    CONF_TARGET_PLAYER,
    DEFAULT_FRIENDLY_NAME,
    DEFAULT_HTTP_PORT,
    TRANSPORT_STATE_PAUSED,
    TRANSPORT_STATE_PLAYING,
    TRANSPORT_STATE_STOPPED,
)
from .renderer import UPnPRenderer
from .ssdp import SSDPAdvertiser

if TYPE_CHECKING:
    from music_assistant.mass import MusicAssistant

LOGGER = logging.getLogger(__name__)


class DLNAReceiverProvider(PluginProvider):
    """DLNA Receiver plugin provider for Music Assistant.

    Exposes MA as a UPnP MediaRenderer on the local network so that
    external apps can send audio streams which are then played on any
    configured MA player.
    """

    def __init__(
        self,
        mass: MusicAssistant,
        config: dict[str, ConfigValueType],
    ) -> None:
        super().__init__()
        self.mass = mass
        self._config = config
        self._renderer: UPnPRenderer | None = None
        self._ssdp: SSDPAdvertiser | None = None
        self._plugin_source: PluginSource | None = None
        self._current_stream_url: str | None = None

    @property
    def supported_features(self) -> tuple[ProviderFeature, ...]:
        """Return supported features."""
        return (ProviderFeature.AUDIO_SOURCE,)

    async def loaded_in_mass(self) -> None:
        """Called when the provider is loaded in Music Assistant."""
        friendly_name = str(
            self._config.get(CONF_FRIENDLY_NAME, DEFAULT_FRIENDLY_NAME)
        )
        bind_ip = str(self._config.get(CONF_BIND_IP, "")) or self._detect_ip()
        http_port = int(self._config.get(CONF_HTTP_PORT, DEFAULT_HTTP_PORT))

        # Create UPnP renderer
        self._renderer = UPnPRenderer(
            friendly_name=friendly_name,
            bind_ip=bind_ip,
            http_port=http_port,
        )

        # Wire callbacks
        self._renderer.on_set_av_transport_uri = self._on_set_transport_uri
        self._renderer.on_play = self._on_play
        self._renderer.on_pause = self._on_pause
        self._renderer.on_stop = self._on_stop
        self._renderer.on_set_volume = self._on_set_volume
        self._renderer.on_set_mute = self._on_set_mute

        # Start HTTP server
        await self._renderer.start()

        # Start SSDP advertisement
        self._ssdp = SSDPAdvertiser(
            udn=self._renderer.udn,
            description_url=self._renderer.description_url,
            bind_ip=bind_ip,
        )
        await self._ssdp.start()

        LOGGER.info(
            "DLNA Receiver '%s' started on %s:%s",
            friendly_name,
            bind_ip,
            http_port,
        )

    async def unload(self) -> None:
        """Unload the provider."""
        if self._ssdp:
            await self._ssdp.stop()
            self._ssdp = None
        if self._renderer:
            await self._renderer.stop()
            self._renderer = None
        LOGGER.info("DLNA Receiver provider unloaded")

    # ------------------------------------------------------------------
    # PluginProvider audio source interface
    # ------------------------------------------------------------------

    async def get_audio_stream(
        self,
        player_id: str,  # noqa: ARG002
    ) -> AsyncGenerator[bytes, None]:
        """Yield audio bytes from the received DLNA stream.

        MA calls this when the plugin source is activated on a player.
        We proxy the external URL through aiohttp and yield raw bytes.
        """
        import aiohttp

        if not self._current_stream_url:
            LOGGER.warning("get_audio_stream called but no stream URL set")
            return

        LOGGER.info("Proxying DLNA stream: %s", self._current_stream_url)
        async with aiohttp.ClientSession() as session:
            async with session.get(self._current_stream_url) as resp:
                async for chunk in resp.content.iter_any():
                    yield chunk
        LOGGER.info("DLNA stream ended")

    # ------------------------------------------------------------------
    # Renderer callbacks
    # ------------------------------------------------------------------

    async def _on_set_transport_uri(
        self, uri: str, metadata: str | None
    ) -> None:
        """Handle SetAVTransportURI from a DLNA control point."""
        LOGGER.info("Received transport URI: %s", uri)
        self._current_stream_url = uri

    async def _on_play(self) -> None:
        """Handle Play action — start streaming to the target player."""
        target = str(self._config.get(CONF_TARGET_PLAYER, ""))
        if not target:
            LOGGER.warning("No target player configured — ignoring Play")
            return

        if not self._current_stream_url:
            LOGGER.warning("Play received but no stream URL available")
            return

        # Register a plugin source and activate it on the target player
        audio_format = AudioFormat(content_type=ContentType.UNKNOWN)
        self._plugin_source = PluginSource(
            id=f"dlna_receiver_{self.instance_id}",
            name="DLNA Receiver",
            audio_format=audio_format,
        )

        LOGGER.info("Starting playback on player %s", target)
        # Use MA streams controller to play the plugin source
        await self.mass.streams.play_plugin_source(
            player_id=target,
            plugin_source=self._plugin_source,
        )

    async def _on_pause(self) -> None:
        """Handle Pause action."""
        target = str(self._config.get(CONF_TARGET_PLAYER, ""))
        if target:
            await self.mass.players.cmd_pause(target)

    async def _on_stop(self) -> None:
        """Handle Stop action."""
        target = str(self._config.get(CONF_TARGET_PLAYER, ""))
        if target:
            await self.mass.players.cmd_stop(target)
        self._current_stream_url = None

    async def _on_set_volume(self, volume: int) -> None:
        """Handle volume change."""
        target = str(self._config.get(CONF_TARGET_PLAYER, ""))
        if target:
            await self.mass.players.cmd_volume_set(target, volume)

    async def _on_set_mute(self, mute: bool) -> None:
        """Handle mute change."""
        target = str(self._config.get(CONF_TARGET_PLAYER, ""))
        if target:
            await self.mass.players.cmd_volume_mute(target, mute)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _detect_ip() -> str:
        """Detect the primary LAN IP address."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(("8.8.8.8", 80))
            ip = sock.getsockname()[0]
            sock.close()
            return ip
        except Exception:
            return "0.0.0.0"
