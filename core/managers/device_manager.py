#!/usr/bin/env python3
# core/managers/device_manager.py
# Connects to PS5, Sends Data, Receives Responses, Feeds about Panel


import socket
import time


class DeviceManager:
    def __init__(self):
        self.connected = False
        self.current_connection = None

    def connect(self, ip: str, port: int) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect((ip, port))
            sock.close()
            self.connected = True
            self.current_connection = (ip, port)
            return True
        except:
            self.connected = False
            return False

    def disconnect(self):
        self.connected = False
        self.current_connection = None

    def is_connected(self) -> bool:
        return self.connected

    def send_data(self, ip: str, port: int, data: bytes) -> bool:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((ip, port))
            sock.sendall(data)
            sock.close()
            return True
        except:
            return False

    def receive_data(self, ip: str, port: int, buffer_size: int = 4096) -> bytes:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((ip, port))
            data = sock.recv(buffer_size)
            sock.close()
            return data
        except:
            return b""

    def get_device_info(self, ip: str, port: int) -> dict:
        return {
            "ip": ip,
            "port": port,
            "connected": self.connected,
            "type": "PS5",
        }

    def get_firmware(self) -> str:
        if self.connected:
            return "Unknown"
        return "Not connected"
