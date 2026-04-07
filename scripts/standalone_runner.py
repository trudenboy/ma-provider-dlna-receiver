#!/usr/bin/env python3
"""Standalone DLNA Renderer runner for integration testing.

Starts a UPnP MediaRenderer + SSDP advertiser without Music Assistant.
Useful for testing discovery and SOAP control from BubbleUPnP, foobar2000, etc.

Usage:
    python scripts/standalone_runner.py [--name NAME] [--ip IP] [--port PORT]
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import signal
import sys
import uuid
from pathlib import Path

# Add project root to path so we can import the provider package
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from provider.renderer import UPnPRenderer
from provider.ssdp import SSDPAdvertiser

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
)
LOGGER = logging.getLogger("standalone_runner")


async def _on_set_uri(uri: str, metadata: str) -> None:
    LOGGER.info(">> SetAVTransportURI: %s", uri)
    if metadata:
        LOGGER.debug("   Metadata: %s", metadata[:200])


async def _on_play() -> None:
    LOGGER.info(">> Play requested")


async def _on_pause() -> None:
    LOGGER.info(">> Pause requested")


async def _on_stop() -> None:
    LOGGER.info(">> Stop requested")


async def _on_set_volume(volume: int) -> None:
    LOGGER.info(">> SetVolume: %d", volume)


async def _on_set_mute(mute: bool) -> None:
    LOGGER.info(">> SetMute: %s", mute)


async def main(name: str, bind_ip: str, port: int) -> None:
    """Run a standalone DLNA renderer for integration testing."""
    udn = f"uuid:{uuid.uuid5(uuid.NAMESPACE_URL, f'ma-dlna-standalone-{name}')}"

    renderer = UPnPRenderer(
        friendly_name=name,
        bind_ip=bind_ip,
        http_port=port,
        udn=udn,
    )
    renderer.on_set_av_transport_uri = _on_set_uri
    renderer.on_play = _on_play
    renderer.on_pause = _on_pause
    renderer.on_stop = _on_stop
    renderer.on_set_volume = _on_set_volume
    renderer.on_set_mute = _on_set_mute

    description_url = f"http://{bind_ip}:{port}/description.xml"
    ssdp = SSDPAdvertiser(udn=udn, description_url=description_url, bind_ip=bind_ip)

    await renderer.start()
    await ssdp.start()

    LOGGER.info("=" * 60)
    LOGGER.info("DLNA Renderer running!")
    LOGGER.info("  Name: %s", name)
    LOGGER.info("  UDN:  %s", udn)
    LOGGER.info("  URL:  %s", description_url)
    LOGGER.info("=" * 60)
    LOGGER.info("Press Ctrl+C to stop")

    stop_event = asyncio.Event()
    loop = asyncio.get_running_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, stop_event.set)

    await stop_event.wait()

    LOGGER.info("Shutting down...")
    await ssdp.stop()
    await renderer.stop()
    LOGGER.info("Done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standalone DLNA Renderer")
    parser.add_argument("--name", default="MA Test Renderer", help="Friendly name")
    parser.add_argument("--ip", default="192.168.10.235", help="Bind IP address")
    parser.add_argument("--port", type=int, default=8298, help="HTTP port")
    args = parser.parse_args()

    asyncio.run(main(args.name, args.ip, args.port))
