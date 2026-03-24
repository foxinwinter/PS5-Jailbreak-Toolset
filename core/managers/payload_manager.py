#!/usr/bin/env python3
# core/managers/payload_manager.py
# Loads payload files, ensures compatibility with Selected Exploit, sends payload via device_manager


import os
import json


class PayloadManager:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.payloads = []
        self.manifest = {}
        self._load_manifest()

    def _load_manifest(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        manifest_path = os.path.join(base_dir, "payloads", "metadata", "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                self.manifest = json.load(f)

    def _get_payloads_dir(self):
        exploit = self.session_manager.get_selected_exploit()
        if not exploit:
            return None
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        return os.path.join(base_dir, "payloads", exploit.lower())

    def list_available_payloads(self) -> list:
        payloads_dir = self._get_payloads_dir()
        if not payloads_dir or not os.path.isdir(payloads_dir):
            return []

        payloads = []
        for f in os.listdir(payloads_dir):
            ext = os.path.splitext(f)[1]
            if ext in [".lua", ".js", ".elf"]:
                payloads.append(f)
        return payloads

    def refresh_payload_list(self):
        self.payloads = self.list_available_payloads()

    def validate_payload(self, payload_path: str, allow_unsafe: bool = False) -> bool:
        if not os.path.exists(payload_path):
            return False

        exploit = self.session_manager.get_selected_exploit()
        if not exploit:
            return False

        ext = os.path.splitext(payload_path)[1]

        manifest_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "payloads",
            "metadata",
            "manifest.json",
        )

        if os.path.exists(manifest_path):
            with open(manifest_path, "r") as f:
                manifest = json.load(f)
                payload_name = os.path.basename(payload_path)
                if payload_name in manifest:
                    payload_info = manifest[payload_name]
                    if payload_info.get("exploit", "").lower() != exploit.lower():
                        if not allow_unsafe:
                            return False

        return True

    def send_payload(self, payload_path: str, device_manager) -> bool:
        if not self.validate_payload(payload_path):
            return False

        target = self.session_manager.get_target_info()
        if not target:
            return False

        with open(payload_path, "rb") as f:
            data = f.read()

        result = device_manager.send_data(target["ip"], target["port"], data)

        if result:
            self.session_manager.set_last_payload(payload_path)

        return result

    def get_last_payload(self) -> str:
        return self.session_manager.get_last_payload()

    def get_payloads_for_exploit(self, exploit: str) -> list:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        exploit_dir = os.path.join(base_dir, "payloads", exploit.lower())
        if not os.path.isdir(exploit_dir):
            return []

        payloads = []
        for f in os.listdir(exploit_dir):
            ext = os.path.splitext(f)[1]
            if ext in [".lua", ".js", ".elf", ".bin"]:
                payloads.append(f)
        return payloads
