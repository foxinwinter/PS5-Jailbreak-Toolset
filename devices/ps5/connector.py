import socket
import threading
import logging
from typing import Optional, Dict, Any
from datetime import datetime

from devices.base import (
    BaseDeviceConnector,
    BaseProtocol,
    ConnectionState,
    DeviceInfo,
    Device,
)


class PS5Connector(BaseDeviceConnector):
    DEFAULT_PORT = 9000
    PAYLOAD_PORT = 9020

    def __init__(self):
        super().__init__()
        self.socket: Optional[socket.socket] = None
        self.lock = threading.Lock()

    def connect(self, address: str, port: int = DEFAULT_PORT) -> bool:
        with self.lock:
            try:
                self.set_state(ConnectionState.CONNECTING)
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.settimeout(10.0)
                self.socket.connect((address, port))

                self.device = Device(
                    address=address,
                    port=port,
                    state=ConnectionState.CONNECTED,
                    last_seen=datetime.now(),
                )

                self.set_state(ConnectionState.CONNECTED)
                return True
            except Exception as e:
                logging.error(f"Failed to connect to PS5 at {address}:{port}: {e}")
                self.set_state(ConnectionState.ERROR)
                return False

    def disconnect(self) -> None:
        with self.lock:
            if self.socket:
                try:
                    self.socket.close()
                except:
                    pass
                self.socket = None
            if self.device:
                self.device.state = ConnectionState.DISCONNECTED
            self.set_state(ConnectionState.DISCONNECTED)

    def send(self, data: bytes) -> bool:
        with self.lock:
            if not self.socket or not self.is_connected():
                return False
            try:
                self.socket.sendall(data)
                return True
            except Exception as e:
                logging.error(f"Failed to send data: {e}")
                self.set_state(ConnectionState.ERROR)
                return False

    def receive(self, size: int = 4096) -> Optional[bytes]:
        with self.lock:
            if not self.socket or not self.is_connected():
                return None
            try:
                self.socket.settimeout(30.0)
                data = self.socket.recv(size)
                return data if data else None
            except Exception as e:
                logging.error(f"Failed to receive data: {e}")
                return None

    def get_info(self) -> DeviceInfo:
        if self.device and self.device.info:
            return self.device.info
        return DeviceInfo(
            device_type="PS5",
            firmware="Unknown",
            hostname="Unknown",
            ip_address=self.device.address if self.device else "Unknown",
        )

    def send_payload(self, payload: bytes) -> bool:
        with self.lock:
            if not self.socket:
                return False
            try:
                payload_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                payload_socket.connect((self.device.address, self.PAYLOAD_PORT))
                payload_socket.sendall(payload)
                payload_socket.close()
                return True
            except Exception as e:
                logging.error(f"Failed to send payload: {e}")
                return False


class PS5Protocol(BaseProtocol):
    def __init__(self, connector: PS5Connector):
        super().__init__(connector)

    def handshake(self) -> bool:
        try:
            response = self.connector.receive(64)
            if response and b"ACK" in response:
                return True
            return False
        except:
            return False

    def authenticate(self, credentials: Optional[Dict[str, str]] = None) -> bool:
        if not credentials:
            auth_data = b"AUTH"
        else:
            auth_data = credentials.get("key", "").encode()

        if self.connector.send(auth_data):
            response = self.connector.receive(64)
            if response and b"OK" in response:
                self.connector.set_state(ConnectionState.AUTHENTICATED)
                return True
        return False

    def send_command(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[bytes]:
        cmd_data = command.encode()
        if self.connector.send(cmd_data):
            return self.connector.receive(4096)
        return None

    def send_file(self, path: str) -> bool:
        try:
            with open(path, "rb") as f:
                data = f.read()
            size = len(data)
            self.connector.send(f"FILE:{size}".encode())
            return self.connector.send(data)
        except Exception as e:
            logging.error(f"Failed to send file: {e}")
            return False

    def recv_file(self, path: str, data: bytes) -> bool:
        try:
            with open(path, "wb") as f:
                f.write(data)
            return True
        except Exception as e:
            logging.error(f"Failed to receive file: {e}")
            return False


def create_connector() -> PS5Connector:
    return PS5Connector()


def create_protocol(connector: PS5Connector) -> PS5Protocol:
    return PS5Protocol(connector)
