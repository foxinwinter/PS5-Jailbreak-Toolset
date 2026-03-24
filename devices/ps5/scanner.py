import socket
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

from devices.ps5.connector import PS5Connector
from devices.ps5.info import PS5DeviceInfo


@dataclass
class ScanResult:
    ip: str
    port: int
    device_type: str
    firmware: Optional[str] = None
    hostname: Optional[str] = None
    available: bool = False


class PS5Scanner:
    DEFAULT_PORTS = [9000, 9020, 8080]
    TIMEOUT = 3.0

    def __init__(self):
        self.results: List[ScanResult] = []

    def scan_host(
        self, ip: str, ports: Optional[List[int]] = None
    ) -> Optional[ScanResult]:
        ports = ports or self.DEFAULT_PORTS

        for port in ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(self.TIMEOUT)
                result = sock.connect_ex((ip, port))
                sock.close()

                if result == 0:
                    return ScanResult(
                        ip=ip, port=port, device_type="PS5", available=True
                    )
            except:
                continue
        return None

    def scan_range(
        self, start_ip: str, end_ip: str, ports: Optional[List[int]] = None
    ) -> List[ScanResult]:
        results = []

        try:
            start_parts = list(map(int, start_ip.split(".")))
            end_parts = list(map(int, end_ip.split(".")))

            for i in range(start_parts[3], end_parts[3] + 1):
                ip = f"{start_parts[0]}.{start_parts[1]}.{start_parts[2]}.{i}"
                result = self.scan_host(ip, ports)
                if result:
                    results.append(result)
        except Exception as e:
            logging.error(f"Scan range error: {e}")

        self.results = results
        return results

    def scan_subnet(
        self, subnet: str, netmask: str = "24", ports: Optional[List[int]] = None
    ) -> List[ScanResult]:
        results = []

        try:
            subnet_parts = list(map(int, subnet.split(".")))
            host_bits = 32 - int(netmask)
            num_hosts = 2**host_bits

            for i in range(1, min(num_hosts, 256)):
                ip = f"{subnet_parts[0]}.{subnet_parts[1]}.{subnet_parts[2]}.{i}"
                result = self.scan_host(ip, ports)
                if result:
                    results.append(result)
        except Exception as e:
            logging.error(f"Subnet scan error: {e}")

        self.results = results
        return results

    def scan_common_ports(self, ip: str) -> Dict[int, bool]:
        results = {}
        common_ports = [21, 22, 23, 80, 443, 9000, 9020, 8080, 9090, 19000]

        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1.0)
                result = sock.connect_ex((ip, port))
                sock.close()
                results[port] = result == 0
            except:
                results[port] = False

        return results

    def get_results(self) -> List[ScanResult]:
        return self.results

    def clear_results(self) -> None:
        self.results.clear()


def scan_for_ps5_devices(
    subnet: str = "192.168.1.0", netmask: int = 24
) -> List[ScanResult]:
    scanner = PS5Scanner()
    return scanner.scan_subnet(subnet, str(netmask))


def quick_check(ip: str) -> bool:
    scanner = PS5Scanner()
    result = scanner.scan_host(ip)
    return result is not None if result else False
