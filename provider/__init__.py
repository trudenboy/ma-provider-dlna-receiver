"""
DLNA Receiver — Music Assistant Plugin Provider.

Exposes Music Assistant as a UPnP/DLNA MediaRenderer so that external
applications (Qobuz, BubbleUPnP, foobar2000, mconnect, etc.) can discover
and cast audio streams to any MA player.

Architecture
~~~~~~~~~~~~
1. SSDP advertisement  — announces a virtual MediaRenderer on the LAN
2. UPnP HTTP server     — serves device/service XML descriptions and
                          accepts SOAP control actions (AVTransport,
                          RenderingControl, ConnectionManager)
3. PluginSource bridge  — received audio URL is fed into the MA streaming
                          pipeline as a PluginSource, routed to the
                          configured target player
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from music_assistant_models.config_entries import ConfigEntry, ConfigValueType
from music_assistant_models.enums import ConfigEntryType

from .constants import (
    CONF_BIND_IP,
    CONF_FRIENDLY_NAME,
    CONF_HTTP_PORT,
    CONF_TARGET_PLAYER,
    DEFAULT_FRIENDLY_NAME,
    DEFAULT_HTTP_PORT,
)

if TYPE_CHECKING:
    from music_assistant.mass import MusicAssistant
    from music_assistant.models import ProviderModuleType

    from .provider import DLNAReceiverProvider


async def get_config_entries(
    mass: MusicAssistant,  # noqa: ARG001
    instance_id: str | None = None,  # noqa: ARG001
    action: str | None = None,  # noqa: ARG001
    values: dict[str, ConfigValueType] | None = None,  # noqa: ARG001
) -> tuple[ConfigEntry, ...]:
    """Return Config entries to setup this provider."""
    return (
        ConfigEntry(
            key=CONF_FRIENDLY_NAME,
            type=ConfigEntryType.STRING,
            label="Friendly name",
            description="Name shown to DLNA control points on the network.",
            default_value=DEFAULT_FRIENDLY_NAME,
            required=True,
        ),
        ConfigEntry(
            key=CONF_TARGET_PLAYER,
            type=ConfigEntryType.STRING,
            label="Target player",
            description=(
                "MA player_id to route received audio to. "
                "Leave empty to select at playback time."
            ),
            required=False,
        ),
        ConfigEntry(
            key=CONF_BIND_IP,
            type=ConfigEntryType.STRING,
            label="Bind IP address",
            description=(
                "IP address to bind the UPnP HTTP server and SSDP listener. "
                "Leave empty to auto-detect."
            ),
            required=False,
        ),
        ConfigEntry(
            key=CONF_HTTP_PORT,
            type=ConfigEntryType.INTEGER,
            label="HTTP port",
            description="Port for the UPnP description / control HTTP server.",
            default_value=DEFAULT_HTTP_PORT,
            required=True,
        ),
    )


async def setup(
    mass: MusicAssistant,
    manifest: dict,  # noqa: ARG001
    config: dict[str, ConfigValueType],
) -> ProviderModuleType:
    """Set up the DLNA Receiver provider."""
    from .provider import DLNAReceiverProvider

    return DLNAReceiverProvider(mass, config)
