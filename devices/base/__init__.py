from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime


class ConnectionState(Enum):
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    AUTHENTICATED = "authenticated"
    ERROR = "error"


@dataclass
class DeviceInfo:
    device_type: str
    firmware: str
    hostname: str
    ip_address: str
    mac_address: Optional[str] = None
    name: Optional[str] = None
    serial: Optional[str] = None
    model: Optional[str] = None


@dataclass
class Device:
    address: str
    port: int
    info: Optional[DeviceInfo] = None
    state: ConnectionState = ConnectionState.DISCONNECTED
    last_seen: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseDeviceConnector(ABC):
    def __init__(self):
        self.device: Optional[Device] = None
        self.state = ConnectionState.DISCONNECTED

    @abstractmethod
    def connect(self, address: str, port: int = 9000) -> bool:
        pass

    @abstractmethod
    def disconnect(self) -> None:
        pass

    @abstractmethod
    def send(self, data: bytes) -> bool:
        pass

    @abstractmethod
    def receive(self, size: int = 4096) -> Optional[bytes]:
        pass

    @abstractmethod
    def get_info(self) -> DeviceInfo:
        pass

    def is_connected(self) -> bool:
        return (
            self.state == ConnectionState.CONNECTED
            or self.state == ConnectionState.AUTHENTICATED
        )

    def set_state(self, state: ConnectionState) -> None:
        self.state = state

    def get_state(self) -> ConnectionState:
        return self.state


class BaseProtocol(ABC):
    def __init__(self, connector: BaseDeviceConnector):
        self.connector = connector

    @abstractmethod
    def handshake(self) -> bool:
        pass

    @abstractmethod
    def authenticate(self, credentials: Optional[Dict[str, str]] = None) -> bool:
        pass

    @abstractmethod
    def send_command(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> Optional[bytes]:
        pass

    @abstractmethod
    def send_file(self, path: str) -> bool:
        pass

    @abstractmethod
    def recv_file(self, path: str, data: bytes) -> bool:
        pass
