import json
import logging
import struct
import os
from socket import socket, AF_INET, SOCK_STREAM
from .log import OpenplanetLog

logger = logging.getLogger(__name__)


class OpenplanetTcpSocket:
    def __init__(self, port: int) -> None:
        self.socket = socket(AF_INET, SOCK_STREAM)
        self.port = port
        self.connected = False

    def try_connect(self) -> bool:
        if self.connected:
            return True

        self.socket.settimeout(0.01)
        try:
            self.socket.connect(("localhost", self.port))
            logger.debug(f"Connected to {str(self.socket)}")
            self.connected = True
        except Exception as e:
            logger.debug(
                f"Error connecting to socket on port {str(self.port)}: {str(e)}"
            )
            self.connected = False
        self.socket.settimeout(None)
        return self.connected

    def send(self, data: "bytes|dict|str") -> bool:
        send_data = data
        if isinstance(data, dict):
            send_data = json.dumps(data).encode()
        elif isinstance(data, str):
            send_data = data.encode()
        count = 0
        try:
            count = self.socket.send(send_data)
            logger.debug(f"Sent {str(count)} bytes")
        except Exception as e:
            self.connected = False
            logger.debug("Error sending data")
        return count > 0

    def receive(self) -> str:
        hdr_bytes = b""
        while len(hdr_bytes) < 4:
            try:
                hdr_bytes += self.socket.recv(4)
            except Exception as e:
                self.connected = False
                logger.debug("Error receiving header bytes")
                return ""
        (data_length,) = struct.unpack("L", hdr_bytes)
        logger.debug(f"Header indicates {str(data_length)} bytes of data")

        data_bytes = b""
        if len(hdr_bytes) > 4:
            logger.debug("Taking some bytes from header to start with in data")
            data_bytes += hdr_bytes[4:]
        while len(data_bytes) < data_length:
            try:
                data_bytes += self.socket.recv(1024)
            except Exception as e:
                self.connected = False
                logger.debug("Error receiving message bytes")
                return ""
        if len(data_bytes) > data_length:
            logger.debug("Trimming data")
            data_bytes = data_bytes[0:data_length]
        return data_bytes.decode()


class RemoteBuildAPI:
    def __init__(self, game: str, port: int) -> None:
        self.game = game
        self.openplanet = OpenplanetTcpSocket(port)
        self.data_folder = ""
        self.app_folder = ""
        self.op_log = OpenplanetLog()

    def send_route(self, route: str, data: dict) -> dict:
        response = {}
        if self.openplanet.try_connect():
            self.openplanet.send({"route": route, "data": data})
            response_text = self.openplanet.receive()
            try:
                response = json.loads(response_text)
            except Exception as e:
                logger.exception(e)
        return response

    def get_status(self) -> bool:
        response = self.send_route("get_status", {})
        status = response.get("data", "")
        return status == "Alive"

    def get_data_folder(self) -> bool:
        if not self.get_status():
            return False

        response = self.send_route("get_data_folder", {})
        response_data_folder = response.get("data", "")
        if os.path.isdir(response_data_folder):
            self.data_folder = response_data_folder
            self.op_log.set_path(os.path.join(self.data_folder, "Openplanet.log"))
        return self.data_folder != ""

    def get_app_folder(self) -> bool:
        if not self.get_status():
            return False

        response = self.send_route("get_app_folder", {})
        response_app_folder = response.get("data", "")
        if os.path.isdir(response_app_folder):
            self.app_folder = response_app_folder
        return self.app_folder != ""

    def load_plugin(self, plugin_id, plugin_src="user", plugin_type="zip") -> bool:
        if not self.get_status():
            return False

        self.op_log.start_monitor()
        response = self.send_route(
            "load_plugin",
            {
                "id": plugin_id,
                "source": plugin_src,
                "type": plugin_type,
            },
        )
        log_msgs = self.op_log.end_monitor()
        for msg in log_msgs:
            if msg.source == "ScriptEngine":
                logger.info(msg.text)
        if response:
            if response.get("error", ""):
                [logger.error(err) for err in response["error"].strip().split("\n")]
        return response.get("error", "") == ""

    def unload_plugin(self, plugin_id) -> bool:
        if not self.get_status():
            return False

        response = self.send_route("unload_plugin", {"id": plugin_id})
        if response:
            if response.get("error", ""):
                [logger.error(err) for err in response["error"].strip().split("\n")]
        return response.get("error", "") == ""
