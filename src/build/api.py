import json
import logging
import struct
from socket import socket, AF_INET, SOCK_STREAM

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
            self.socket.connect(('localhost', self.port))
            logger.debug(f"Connected to {str(self.socket)}")
            self.connected = True
        except Exception as e:
            logger.debug(f'Error connecting to socket on port {str(self.port)}: {str(e)}')
            self.connected = False
        self.socket.settimeout(None)
        return self.connected

    def send(self, data: 'bytes|dict|str') -> bool:
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
        hdr_bytes = b''
        while len(hdr_bytes) < 4:
            try:
                hdr_bytes += self.socket.recv(4)
            except Exception as e:
                self.connected = False
                logger.debug("Error receiving header bytes")
                return ''
        (data_length, ) = struct.unpack("L", hdr_bytes)
        logger.debug(f"Header indicates {str(data_length)} bytes of data")

        data_bytes = b''
        if len(hdr_bytes) > 4:
            logger.debug("Taking some bytes from header to start with in data")
            data_bytes += hdr_bytes[4:]
        while len(data_bytes) < data_length:
            try:
                data_bytes += self.socket.recv(1024)
            except Exception as e:
                self.connected = False
                logger.debug("Error receiving message bytes")
                return ''
        if len(data_bytes) > data_length:
            logger.debug("Trimming data")
            data_bytes = data_bytes[0:data_length]
        return data_bytes.decode()


class HotReloadAPI:
    def __init__(self, game: str, port: int) -> None:
        self.game = game
        self.openplanet = OpenplanetTcpSocket(port)

    def send_route(self, route: str, data: dict) -> str:
        response = ''
        if self.openplanet.try_connect():
            self.openplanet.send({'route': route, 'data': data})
            response = self.openplanet.receive()
        return response
