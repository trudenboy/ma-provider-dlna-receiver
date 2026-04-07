"""Tests for the UPnP renderer SOAP handling."""

from __future__ import annotations

import pytest
from aiohttp import web
from aiohttp.test_utils import AioHTTPTestCase, TestClient, TestServer

from provider.renderer import UPnPRenderer


@pytest.fixture
def renderer() -> UPnPRenderer:
    """Create a test renderer instance."""
    return UPnPRenderer(
        friendly_name="Test Renderer",
        bind_ip="127.0.0.1",
        http_port=0,  # will use aiohttp test server
    )


@pytest.fixture
async def client(renderer: UPnPRenderer) -> TestClient:
    """Create an aiohttp test client for the renderer."""
    server = TestServer(renderer._app)
    _client = TestClient(server)
    await _client.start_server()
    yield _client
    await _client.close()


async def test_device_description(client: TestClient) -> None:
    resp = await client.get("/description.xml")
    assert resp.status == 200
    text = await resp.text()
    assert "MediaRenderer" in text
    assert "Test Renderer" in text


async def test_get_transport_info(client: TestClient) -> None:
    resp = await client.post(
        "/AVTransport/control",
        headers={
            "SOAPACTION": '"urn:schemas-upnp-org:service:AVTransport:1#GetTransportInfo"',
        },
        data="<dummy/>",
    )
    assert resp.status == 200
    text = await resp.text()
    assert "NO_MEDIA_PRESENT" in text


async def test_set_volume(client: TestClient, renderer: UPnPRenderer) -> None:
    volume_received = []
    renderer.on_set_volume = lambda v: volume_received.append(v)

    resp = await client.post(
        "/RenderingControl/control",
        headers={
            "SOAPACTION": '"urn:schemas-upnp-org:service:RenderingControl:1#SetVolume"',
        },
        data='<DesiredVolume>75</DesiredVolume>',
    )
    assert resp.status == 200
    assert renderer.volume == 75


async def test_get_protocol_info(client: TestClient) -> None:
    resp = await client.post(
        "/ConnectionManager/control",
        headers={
            "SOAPACTION": '"urn:schemas-upnp-org:service:ConnectionManager:1#GetProtocolInfo"',
        },
        data="<dummy/>",
    )
    assert resp.status == 200
    text = await resp.text()
    assert "audio/flac" in text
