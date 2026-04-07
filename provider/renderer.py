"""DLNA Receiver — UPnP MediaRenderer implementation.

This module contains the HTTP server that serves UPnP device/service XML
descriptions and processes incoming SOAP control actions from DLNA
control points.
"""

from __future__ import annotations

import asyncio
import logging
import uuid
from typing import TYPE_CHECKING, Any
from xml.etree.ElementTree import Element, SubElement, tostring

from aiohttp import web

from .constants import (
    DEFAULT_HTTP_PORT,
    SUPPORTED_MIME_TYPES,
    TRANSPORT_STATE_NO_MEDIA,
    TRANSPORT_STATE_PAUSED,
    TRANSPORT_STATE_PLAYING,
    TRANSPORT_STATE_STOPPED,
    TRANSPORT_STATE_TRANSITIONING,
    UPNP_DEVICE_TYPE,
    UPNP_SERVICE_AV_TRANSPORT,
    UPNP_SERVICE_CONNECTION_MANAGER,
    UPNP_SERVICE_RENDERING_CONTROL,
)

if TYPE_CHECKING:
    pass

LOGGER = logging.getLogger(__name__)


class UPnPRenderer:
    """Virtual UPnP MediaRenderer with SOAP action handling."""

    def __init__(
        self,
        friendly_name: str,
        bind_ip: str,
        http_port: int = DEFAULT_HTTP_PORT,
        udn: str | None = None,
    ) -> None:
        self.friendly_name = friendly_name
        self.bind_ip = bind_ip
        self.http_port = http_port
        self.udn = udn or f"uuid:{uuid.uuid4()}"

        # Transport state
        self.transport_state: str = TRANSPORT_STATE_NO_MEDIA
        self.current_uri: str = ""
        self.current_uri_metadata: str = ""
        self.volume: int = 50
        self.mute: bool = False

        # HTTP server
        self._app = web.Application()
        self._runner: web.AppRunner | None = None
        self._setup_routes()

        # Callbacks (set by provider)
        self.on_set_av_transport_uri: Any = None
        self.on_play: Any = None
        self.on_pause: Any = None
        self.on_stop: Any = None
        self.on_set_volume: Any = None
        self.on_set_mute: Any = None

    def _setup_routes(self) -> None:
        """Register HTTP routes for UPnP description and control."""
        self._app.router.add_get("/description.xml", self._handle_description)
        self._app.router.add_get(
            "/AVTransport/description.xml", self._handle_av_transport_scpd
        )
        self._app.router.add_get(
            "/RenderingControl/description.xml",
            self._handle_rendering_control_scpd,
        )
        self._app.router.add_get(
            "/ConnectionManager/description.xml",
            self._handle_connection_manager_scpd,
        )
        self._app.router.add_post("/AVTransport/control", self._handle_av_transport)
        self._app.router.add_post(
            "/RenderingControl/control", self._handle_rendering_control
        )
        self._app.router.add_post(
            "/ConnectionManager/control", self._handle_connection_manager
        )

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    async def start(self) -> None:
        """Start the UPnP HTTP server."""
        self._runner = web.AppRunner(self._app)
        await self._runner.setup()
        site = web.TCPSite(self._runner, self.bind_ip, self.http_port)
        await site.start()
        LOGGER.info(
            "UPnP renderer HTTP server listening on %s:%s",
            self.bind_ip,
            self.http_port,
        )

    async def stop(self) -> None:
        """Stop the UPnP HTTP server."""
        if self._runner:
            await self._runner.cleanup()
            self._runner = None
        LOGGER.info("UPnP renderer HTTP server stopped")

    @property
    def description_url(self) -> str:
        """Return the device description URL."""
        return f"http://{self.bind_ip}:{self.http_port}/description.xml"

    # ------------------------------------------------------------------
    # UPnP Device Description
    # ------------------------------------------------------------------

    async def _handle_description(self, _request: web.Request) -> web.Response:
        """Return the root UPnP device description XML."""
        root = Element("root", xmlns="urn:schemas-upnp-org:device-1-0")
        spec = SubElement(root, "specVersion")
        SubElement(spec, "major").text = "1"
        SubElement(spec, "minor").text = "0"

        device = SubElement(root, "device")
        SubElement(device, "deviceType").text = UPNP_DEVICE_TYPE
        SubElement(device, "friendlyName").text = self.friendly_name
        SubElement(device, "manufacturer").text = "Music Assistant"
        SubElement(device, "modelName").text = "DLNA Receiver"
        SubElement(device, "modelDescription").text = (
            "Music Assistant DLNA Receiver Bridge"
        )
        SubElement(device, "UDN").text = self.udn

        service_list = SubElement(device, "serviceList")
        for svc_type, svc_id, scpd_url, ctrl_url, event_url in [
            (
                UPNP_SERVICE_AV_TRANSPORT,
                "urn:upnp-org:serviceId:AVTransport",
                "/AVTransport/description.xml",
                "/AVTransport/control",
                "/AVTransport/event",
            ),
            (
                UPNP_SERVICE_RENDERING_CONTROL,
                "urn:upnp-org:serviceId:RenderingControl",
                "/RenderingControl/description.xml",
                "/RenderingControl/control",
                "/RenderingControl/event",
            ),
            (
                UPNP_SERVICE_CONNECTION_MANAGER,
                "urn:upnp-org:serviceId:ConnectionManager",
                "/ConnectionManager/description.xml",
                "/ConnectionManager/control",
                "/ConnectionManager/event",
            ),
        ]:
            svc = SubElement(service_list, "service")
            SubElement(svc, "serviceType").text = svc_type
            SubElement(svc, "serviceId").text = svc_id
            SubElement(svc, "SCPDURL").text = scpd_url
            SubElement(svc, "controlURL").text = ctrl_url
            SubElement(svc, "eventSubURL").text = event_url

        xml_bytes = b'<?xml version="1.0"?>' + tostring(root, encoding="unicode").encode()
        return web.Response(body=xml_bytes, content_type="text/xml")

    # ------------------------------------------------------------------
    # Service SCPDs (minimal stubs — enough for DLNA control points)
    # ------------------------------------------------------------------

    async def _handle_av_transport_scpd(self, _request: web.Request) -> web.Response:
        """Return AVTransport service description."""
        xml = self._build_scpd(
            actions=[
                "SetAVTransportURI",
                "GetTransportInfo",
                "Play",
                "Pause",
                "Stop",
                "GetPositionInfo",
                "GetMediaInfo",
            ]
        )
        return web.Response(body=xml, content_type="text/xml")

    async def _handle_rendering_control_scpd(
        self, _request: web.Request
    ) -> web.Response:
        """Return RenderingControl service description."""
        xml = self._build_scpd(
            actions=["GetVolume", "SetVolume", "GetMute", "SetMute"]
        )
        return web.Response(body=xml, content_type="text/xml")

    async def _handle_connection_manager_scpd(
        self, _request: web.Request
    ) -> web.Response:
        """Return ConnectionManager service description."""
        xml = self._build_scpd(
            actions=["GetProtocolInfo", "GetCurrentConnectionIDs"]
        )
        return web.Response(body=xml, content_type="text/xml")

    @staticmethod
    def _build_scpd(actions: list[str]) -> bytes:
        """Build a minimal SCPD XML with the given action names."""
        root = Element("scpd", xmlns="urn:schemas-upnp-org:service-1-0")
        spec = SubElement(root, "specVersion")
        SubElement(spec, "major").text = "1"
        SubElement(spec, "minor").text = "0"
        action_list = SubElement(root, "actionList")
        for name in actions:
            action = SubElement(action_list, "action")
            SubElement(action, "name").text = name
        SubElement(root, "serviceStateTable")
        return b'<?xml version="1.0"?>' + tostring(root, encoding="unicode").encode()

    # ------------------------------------------------------------------
    # SOAP Action Handlers
    # ------------------------------------------------------------------

    async def _handle_av_transport(self, request: web.Request) -> web.Response:
        """Handle AVTransport SOAP actions."""
        body = await request.text()
        soap_action = request.headers.get("SOAPACTION", "").strip('"')
        action_name = soap_action.rsplit("#", 1)[-1] if "#" in soap_action else ""
        LOGGER.debug("AVTransport action: %s", action_name)

        if action_name == "SetAVTransportURI":
            uri = self._extract_xml_value(body, "CurrentURI")
            metadata = self._extract_xml_value(body, "CurrentURIMetaData")
            self.current_uri = uri or ""
            self.current_uri_metadata = metadata or ""
            self.transport_state = TRANSPORT_STATE_STOPPED
            if self.on_set_av_transport_uri:
                await self.on_set_av_transport_uri(self.current_uri, metadata)
            return self._soap_response(action_name, UPNP_SERVICE_AV_TRANSPORT)

        if action_name == "Play":
            self.transport_state = TRANSPORT_STATE_PLAYING
            if self.on_play:
                await self.on_play()
            return self._soap_response(action_name, UPNP_SERVICE_AV_TRANSPORT)

        if action_name == "Pause":
            self.transport_state = TRANSPORT_STATE_PAUSED
            if self.on_pause:
                await self.on_pause()
            return self._soap_response(action_name, UPNP_SERVICE_AV_TRANSPORT)

        if action_name == "Stop":
            self.transport_state = TRANSPORT_STATE_STOPPED
            if self.on_stop:
                await self.on_stop()
            return self._soap_response(action_name, UPNP_SERVICE_AV_TRANSPORT)

        if action_name == "GetTransportInfo":
            return self._soap_response(
                action_name,
                UPNP_SERVICE_AV_TRANSPORT,
                {
                    "CurrentTransportState": self.transport_state,
                    "CurrentTransportStatus": "OK",
                    "CurrentSpeed": "1",
                },
            )

        if action_name == "GetPositionInfo":
            return self._soap_response(
                action_name,
                UPNP_SERVICE_AV_TRANSPORT,
                {
                    "Track": "1",
                    "TrackDuration": "00:00:00",
                    "TrackMetaData": self.current_uri_metadata,
                    "TrackURI": self.current_uri,
                    "RelTime": "00:00:00",
                    "AbsTime": "00:00:00",
                    "RelCount": "0",
                    "AbsCount": "0",
                },
            )

        if action_name == "GetMediaInfo":
            return self._soap_response(
                action_name,
                UPNP_SERVICE_AV_TRANSPORT,
                {
                    "NrTracks": "1",
                    "MediaDuration": "00:00:00",
                    "CurrentURI": self.current_uri,
                    "CurrentURIMetaData": self.current_uri_metadata,
                    "NextURI": "",
                    "NextURIMetaData": "",
                    "PlayMedium": "NETWORK",
                    "RecordMedium": "NOT_IMPLEMENTED",
                    "WriteStatus": "NOT_IMPLEMENTED",
                },
            )

        LOGGER.warning("Unhandled AVTransport action: %s", action_name)
        return self._soap_error(401, "Invalid Action")

    async def _handle_rendering_control(self, request: web.Request) -> web.Response:
        """Handle RenderingControl SOAP actions."""
        body = await request.text()
        soap_action = request.headers.get("SOAPACTION", "").strip('"')
        action_name = soap_action.rsplit("#", 1)[-1] if "#" in soap_action else ""
        LOGGER.debug("RenderingControl action: %s", action_name)

        if action_name == "GetVolume":
            return self._soap_response(
                action_name,
                UPNP_SERVICE_RENDERING_CONTROL,
                {"CurrentVolume": str(self.volume)},
            )

        if action_name == "SetVolume":
            vol_str = self._extract_xml_value(body, "DesiredVolume")
            if vol_str is not None:
                self.volume = max(0, min(100, int(vol_str)))
                if self.on_set_volume:
                    await self.on_set_volume(self.volume)
            return self._soap_response(
                action_name, UPNP_SERVICE_RENDERING_CONTROL
            )

        if action_name == "GetMute":
            return self._soap_response(
                action_name,
                UPNP_SERVICE_RENDERING_CONTROL,
                {"CurrentMute": "1" if self.mute else "0"},
            )

        if action_name == "SetMute":
            mute_str = self._extract_xml_value(body, "DesiredMute")
            if mute_str is not None:
                self.mute = mute_str in ("1", "true", "True")
                if self.on_set_mute:
                    await self.on_set_mute(self.mute)
            return self._soap_response(
                action_name, UPNP_SERVICE_RENDERING_CONTROL
            )

        LOGGER.warning("Unhandled RenderingControl action: %s", action_name)
        return self._soap_error(401, "Invalid Action")

    async def _handle_connection_manager(self, request: web.Request) -> web.Response:
        """Handle ConnectionManager SOAP actions."""
        soap_action = request.headers.get("SOAPACTION", "").strip('"')
        action_name = soap_action.rsplit("#", 1)[-1] if "#" in soap_action else ""
        LOGGER.debug("ConnectionManager action: %s", action_name)

        if action_name == "GetProtocolInfo":
            sink_protocols = ",".join(
                f"http-get:*:{mime}:*" for mime in SUPPORTED_MIME_TYPES
            )
            return self._soap_response(
                action_name,
                UPNP_SERVICE_CONNECTION_MANAGER,
                {"Source": "", "Sink": sink_protocols},
            )

        if action_name == "GetCurrentConnectionIDs":
            return self._soap_response(
                action_name,
                UPNP_SERVICE_CONNECTION_MANAGER,
                {"ConnectionIDs": "0"},
            )

        LOGGER.warning("Unhandled ConnectionManager action: %s", action_name)
        return self._soap_error(401, "Invalid Action")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_xml_value(xml_str: str, tag: str) -> str | None:
        """Extract a value from a SOAP XML body by tag name (naive parser)."""
        import re

        pattern = rf"<[^>]*{tag}[^>]*>(.*?)</[^>]*{tag}>"
        match = re.search(pattern, xml_str, re.DOTALL)
        return match.group(1) if match else None

    @staticmethod
    def _soap_response(
        action_name: str,
        service_type: str,
        values: dict[str, str] | None = None,
    ) -> web.Response:
        """Build a UPnP SOAP response envelope."""
        body = f"""<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
            s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:{action_name}Response xmlns:u="{service_type}">"""
        if values:
            for key, val in values.items():
                body += f"\n      <{key}>{val}</{key}>"
        body += f"""
    </u:{action_name}Response>
  </s:Body>
</s:Envelope>"""
        return web.Response(body=body, content_type='text/xml; charset="utf-8"')

    @staticmethod
    def _soap_error(code: int, description: str) -> web.Response:
        """Build a UPnP SOAP error response."""
        body = f"""<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"
            s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <s:Fault>
      <faultcode>s:Client</faultcode>
      <faultstring>UPnPError</faultstring>
      <detail>
        <UPnPError xmlns="urn:schemas-upnp-org:control-1-0">
          <errorCode>{code}</errorCode>
          <errorDescription>{description}</errorDescription>
        </UPnPError>
      </detail>
    </s:Fault>
  </s:Body>
</s:Envelope>"""
        return web.Response(
            body=body,
            status=500,
            content_type='text/xml; charset="utf-8"',
        )
