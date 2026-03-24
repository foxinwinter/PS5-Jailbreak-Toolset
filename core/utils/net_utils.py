import socket
import struct
import threading
import time
from typing import Optional, Tuple


class NetUtils:
    @staticmethod
    def create_tcp_server(host: str, port: int, backlog: int = 5) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(backlog)
        return sock

    @staticmethod
    def create_tcp_client(host: str, port: int, timeout: float = 10.0) -> socket.socket:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        return sock

    @staticmethod
    def send_data(sock: socket.socket, data: bytes) -> int:
        return sock.sendall(data)

    @staticmethod
    def recv_data(
        sock: socket.socket, size: int, timeout: float = 10.0
    ) -> Optional[bytes]:
        sock.settimeout(timeout)
        try:
            data = b""
            while len(data) < size:
                chunk = sock.recv(size - len(data))
                if not chunk:
                    return None
                data += chunk
            return data
        except socket.timeout:
            return None

    @staticmethod
    def recv_until(
        sock: socket.socket, delimiter: bytes, timeout: float = 10.0
    ) -> Optional[bytes]:
        sock.settimeout(timeout)
        try:
            data = b""
            while delimiter not in data:
                chunk = sock.recv(4096)
                if not chunk:
                    return None
                data += chunk
            return data
        except socket.timeout:
            return None

    @staticmethod
    def pack_uint32(value: int) -> bytes:
        return struct.pack(">I", value)

    @staticmethod
    def unpack_uint32(data: bytes) -> int:
        return struct.unpack(">I", data)[0]

    @staticmethod
    def pack_uint64(value: int) -> bytes:
        return struct.pack(">Q", value)

    @staticmethod
    def unpack_uint64(data: bytes) -> int:
        return struct.unpack(">Q", data)[0]

    @staticmethod
    def check_port_available(host: str, port: int) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind((host, port))
            sock.close()
            return True
        except OSError:
            return False

    @staticmethod
    def find_available_port(
        host: str, start_port: int, max_attempts: int = 100
    ) -> Optional[int]:
        for port in range(start_port, start_port + max_attempts):
            if NetUtils.check_port_available(host, port):
                return port
        return None


class UDPServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.running = False
        self.handlers = []

    def start(self):
        self.sock.bind((self.host, self.port))
        self.sock.settimeout(1.0)
        self.running = True
        self._receive_loop()

    def stop(self):
        self.running = False
        self.sock.close()

    def add_handler(self, handler):
        self.handlers.append(handler)

    def _receive_loop(self):
        while self.running:
            try:
                data, addr = self.sock.recvfrom(65535)
                for handler in self.handlers:
                    handler(data, addr)
            except socket.timeout:
                continue
            except Exception:
                pass


class TCPClientPool:
    def __init__(self, max_connections: int = 10):
        self.max_connections = max_connections
        self.connections = {}
        self.lock = threading.Lock()

    def get_connection(self, host: str, port: int) -> Optional[socket.socket]:
        key = f"{host}:{port}"
        with self.lock:
            if key in self.connections:
                sock = self.connections[key]
                try:
                    sock.send(b"")
                    return sock
                except:
                    del self.connections[key]
            return None

    def add_connection(self, host: str, port: int, sock: socket.socket):
        key = f"{host}:{port}"
        with self.lock:
            if len(self.connections) < self.max_connections:
                self.connections[key] = sock

    def close_all(self):
        with self.lock:
            for sock in self.connections.values():
                try:
                    sock.close()
                except:
                    pass
            self.connections.clear()
