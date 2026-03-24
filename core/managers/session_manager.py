#!/usr/bin/env python3
# core/managers/session_manager.py
# Tracks: Session ID, Selected Payload, active device, last sent payload, selected exploit


import os
import time
import random
import string
import json


class SessionManager:
    def __init__(self):
        self.session_id = None
        self.selected_payload = None
        self.active_device = None
        self.last_sent_payload = None
        self.selected_exploit = None
        self.session_start_time = None
        self.connection_time = None
        self.target_info = {}
        self._load_config()

    def _load_config(self):
        config_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "config"
        )
        os.makedirs(config_dir, exist_ok=True)
        self.config_file = os.path.join(config_dir, "session.json")
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                self.target_info = json.load(f)

    def _save_config(self):
        config_dir = os.path.dirname(self.config_file)
        os.makedirs(config_dir, exist_ok=True)
        with open(self.config_file, "w") as f:
            json.dump(self.target_info, f)

    def generate_session_id(self) -> str:
        while True:
            new_id = "".join(
                random.choices(string.ascii_lowercase + string.digits, k=6)
            )
            if new_id != self.session_id:
                break
        self.session_id = new_id
        self.session_start_time = time.time()
        return new_id

    def kill_session(self) -> str:
        if self.session_id:
            old_id = self.session_id
            self.session_id = None
            self.session_start_time = None
            self.connection_time = None
            return f"Session {old_id} terminated."
        return "No active session."

    def get_session_id(self) -> str:
        return self.session_id

    def get_uptime(self) -> str:
        if not self.session_start_time:
            return "No active session"
        elapsed = int(time.time() - self.session_start_time)
        minutes, seconds = divmod(elapsed, 60)
        return f"{minutes}m {seconds}s"

    def get_connection_time(self) -> str:
        if not self.connection_time:
            return "Not connected"
        return self.connection_time

    def set_target(self, ip: str, port: int):
        self.target_info = {"ip": ip, "port": port}
        self._save_config()

    def get_target_info(self) -> dict:
        return self.target_info

    def set_selected_payload(self, payload: str):
        self.selected_payload = payload

    def get_selected_payload(self) -> str:
        return self.selected_payload

    def set_last_payload(self, payload: str):
        self.last_sent_payload = payload

    def get_last_payload(self) -> str:
        return self.last_sent_payload

    def set_selected_exploit(self, exploit: str):
        self.selected_exploit = exploit

    def get_selected_exploit(self) -> str:
        return self.selected_exploit

    def set_connection_time(self, timestamp: str):
        self.connection_time = timestamp

    def get_active_sessions(self) -> list:
        if self.session_id:
            return [self.session_id]
        return []

    def set_last_action(self, action: str):
        self.last_action = action

    def get_last_action(self) -> str:
        return (
            self.last_action
            if hasattr(self, "last_action") and self.last_action
            else "None"
        )
