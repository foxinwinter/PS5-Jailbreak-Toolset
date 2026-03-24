from typing import Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class PS5Info:
    firmware: str
    firmware_version: str
    serial: str
    model: str
    cpu: str
    gpu: str
    ram: str
    storage: str
    bd_key: Optional[str] = None


class PS5DeviceInfo:
    FIRMWARE_SUPPORTED = [
        "4.03",
        "4.50",
        "5.00",
        "5.50",
        "5.70",
        "6.00",
        "6.20",
        "7.00",
        "7.50",
        "8.00",
    ]
    FIRMWARE_LEGACY = ["1.00", "1.02", "1.05", "2.00", "2.50", "3.00", "3.50", "4.00"]

    @staticmethod
    def get_firmware_info(firmware: str) -> Dict[str, Any]:
        info = {
            "version": firmware,
            "supported": firmware in PS5DeviceInfo.FIRMWARE_SUPPORTED,
            "legacy": firmware in PS5DeviceInfo.FIRMWARE_LEGACY,
            "exploitable": firmware in PS5DeviceInfo.FIRMWARE_SUPPORTED,
        }
        return info

    @staticmethod
    def is_firmware_supported(firmware: str) -> bool:
        return firmware in PS5DeviceInfo.FIRMWARE_SUPPORTED

    @staticmethod
    def get_exploit_for_firmware(firmware: str) -> Optional[str]:
        if firmware in PS5DeviceInfo.FIRMWARE_SUPPORTED:
            return "Luac0re"
        return None

    @staticmethod
    def parse_firmware_version(version_string: str) -> Optional[str]:
        try:
            parts = version_string.split(".")
            if len(parts) >= 2:
                return f"{parts[0]}.{parts[1]}"
        except:
            pass
        return None


def get_device_info() -> PS5Info:
    return PS5Info(
        firmware="Unknown",
        firmware_version="Unknown",
        serial="Unknown",
        model="CFI-1xxx",
        cpu="AMD Zen 2",
        gpu="AMD RDNA 2",
        ram="16GB GDDR6",
        storage="825GB SSD",
    )
