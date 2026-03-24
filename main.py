#!/usr/bin/env python3

import sys
import os
import urwid
import threading
import time
import socket
import json
import hashlib
import random
import string
import platform
from datetime import datetime
from typing import Optional, Dict, Any, List

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.command.parser import CommandParser
from core.command.router import CommandRouter
from core.managers.session_manager import SessionManager
from core.managers.payload_manager import PayloadManager
from core.managers.exploit_manager import ExploitManager
from core.managers.log_manager import LogManager
from core.managers.device_manager import DeviceManager
from core.utils.format_utils import FormatUtils


class EMBERUI:
    VERSION = "2.0.0"
    BUILD = "alpha"

    def __init__(self):
        self.session_manager = SessionManager()
        self.payload_manager = PayloadManager()
        self.exploit_manager = ExploitManager()
        self.log_manager = LogManager()
        self.device_manager = DeviceManager()

        self.parser = CommandParser()
        self.router = CommandRouter(
            self.session_manager,
            self.payload_manager,
            self.exploit_manager,
            self.log_manager,
            self.device_manager,
        )

        self.log_output: List[str] = []
        self.target_ip = ""
        self.target_port = 9000
        self.logging_port = 9090
        self.logserver_pid = None
        self.current_exploit = None
        self.last_payload = None
        self.debug_mode = False
        self.unsafe_mode = False
        self.logs_paused = False

        self._generate_session_id()
        self._setup_ui()

    def _generate_session_id(self):
        while True:
            sid = "".join(random.choices(string.ascii_lowercase + string.digits, k=6))
            if sid not in self.session_manager.get_active_sessions():
                self.session_id = sid
                break

    def _setup_ui(self):
        self.palette = {
            "header": "light cyan",
            "log_output": "white",
            "status": "light gray",
            "sync": "light gray",
            "about": "light gray",
            "payload": "light gray",
            "command": "light green",
            "button": "light cyan",
            "button_focus": "white",
        }

    def get_target_info(self) -> Dict[str, Any]:
        return {
            "ip": self.target_ip,
            "port": self.target_port,
            "connected": self.device_manager.is_connected(),
            "firmware": self.device_manager.get_firmware()
            if self.device_manager.is_connected()
            else "Unknown",
        }

    def get_sync_info(self) -> Dict[str, Any]:
        return {
            "luac0re": {
                "repo": "https://github.com/Gezine/luac0re.git",
                "latest": "unknown",
            },
            "y2jb": {"repo": "https://github.com/Gezine/Y2JB.git", "latest": "unknown"},
        }

    def get_about_info(self) -> Dict[str, Any]:
        return {
            "os": platform.system() + " " + platform.release(),
            "logging_port": self.logging_port,
            "target_ip": self.target_ip or "Not set",
            "target_port": self.target_port,
            "author": "foxinwinter",
            "repo": "https://github.com/EmberSystems/E.M.B.E.R",
            "version": self.VERSION,
            "build": self.BUILD,
        }

    def add_log(self, message: str):
        if not self.logs_paused:
            timestamp = FormatUtils.timestamp()
            self.log_output.append(f"[{self.session_id}] {message}")
            if len(self.log_output) > 100:
                self.log_output.pop(0)

    def get_payload_list(self) -> List[str]:
        if not self.current_exploit:
            return []
        return self.payload_manager.get_payloads_for_exploit(self.current_exploit)

    def get_status_info(self) -> Dict[str, Any]:
        return {
            "state": "Connected"
            if self.device_manager.is_connected()
            else "Not Connected",
            "log_server": f"Running ({self.logserver_pid})"
            if self.logserver_pid
            else "Stopped",
            "last_sent_payload": self.last_payload or "None",
            "last_action": self.session_manager.get_last_action() or "None",
        }


class LogOutputBox(urwid.ListBox):
    def __init__(self, ui: EMBERUI):
        self.ui = ui
        self.content = []
        super().__init__(self.content)

    def refresh(self):
        self.content = []
        for log in self.ui.log_output[-50:]:
            self.content.append(urwid.Text(log))
        super().__init__(self.content)


class StatusBox(urwid.WidgetWrap):
    def __init__(self, ui: EMBERUI):
        self.ui = ui
        self._w = self._build()

    def _build(self):
        status = self.ui.get_status_info()

        content = [
            urwid.Text(("header", " /Status")),
            urwid.Divider(),
            urwid.Text(f"State: {status['state']}"),
            urwid.Text(f"Log Server: {status['log_server']}"),
            urwid.Text(f"Last Sent Payload: {status['last_sent_payload']}"),
            urwid.Text(f"Last Action: {status['last_action']}"),
            urwid.Divider(),
            urwid.Text(("header", " /Quick-Actions")),
            urwid.Divider(),
        ]

        return urwid.ListBox(content)


class SyncBox(urwid.WidgetWrap):
    def __init__(self, ui: EMBERUI):
        self.ui = ui
        self._w = self._build()

    def _build(self):
        sync = self.ui.get_sync_info()

        content = [
            urwid.Text(("header", " /Sync")),
            urwid.Divider(),
            urwid.Text("Payloads: Loaded"),
            urwid.Text(f"Luac0re: {sync['luac0re']['latest']}"),
            urwid.Text(f"Y2JB: {sync['y2jb']['latest']}"),
        ]

        return urwid.ListBox(content)


class AboutBox(urwid.WidgetWrap):
    def __init__(self, ui: EMBERUI):
        self.ui = ui
        self._w = self._build()

    def _build(self):
        about = self.ui.get_about_info()

        content = [
            urwid.Text(("header", " /About")),
            urwid.Divider(),
            urwid.Text(("header", " --- Host ---")),
            urwid.Text(f"OS: {about['os']}"),
            urwid.Text(f"Logging Port: {about['logging_port']}"),
            urwid.Divider(),
            urwid.Text(("header", " --- Target ---")),
            urwid.Text(f"Target IP: {about['target_ip']}"),
            urwid.Text(f"Target Port: {about['target_port']}"),
            urwid.Divider(),
            urwid.Text(("header", " --- E.M.B.E.R ---")),
            urwid.Text(f"Version: {about['version']}"),
            urwid.Text(f"Build: {about['build']}"),
            urwid.Divider(),
            urwid.Text(("header", " --- Info ---")),
            urwid.Text(f"Developer: {about['author']}"),
            urwid.Text(f"Repo: {about['repo']}"),
        ]

        return urwid.ListBox(content)


class PayloadExplorerBox(urwid.WidgetWrap):
    def __init__(self, ui: EMBERUI):
        self.ui = ui
        self._w = self._build()

    def _build(self):
        payloads = self.ui.get_payload_list()

        content = [
            urwid.Text(("header", " /Payload Explorer")),
            urwid.Divider(),
        ]

        for p in payloads:
            content.append(urwid.Text(f"{p} [send] [edit]"))

        return urwid.ListBox(content)


class CommandPromptBox(urwid.WidgetWrap):
    def __init__(self, ui: EMBERUI):
        self.ui = ui
        self._w = self._build()

    def _build(self):
        content = [
            urwid.Text(("header", " /Command Prompt")),
            urwid.Divider(),
        ]
        return urwid.ListBox(content)


class EMBERApplication:
    def __init__(self):
        self.ui = EMBERUI()
        self.loop = None
        self.command_history = []
        self.history_index = -1

    def on_input(self, key):
        if key == "enter":
            self.execute_command(self.command_edit.get_edit_text())
            self.command_edit.set_edit_text("")
        elif key == "up":
            if self.history_index < len(self.command_history) - 1:
                self.history_index += 1
                self.command_edit.set_edit_text(
                    self.command_history[self.history_index]
                )
        elif key == "down":
            if self.history_index > 0:
                self.history_index -= 1
                self.command_edit.set_edit_text(
                    self.command_history[self.history_index]
                )
        elif key == "ctrl c":
            raise urwid.ExitMainLoop()

    def execute_command(self, cmd: str):
        if not cmd.strip():
            return

        self.command_history.append(cmd)
        self.history_index = len(self.command_history)

        self.ui.add_log(f"> {cmd}")

        try:
            parsed = self.ui.parser.parse(cmd)
            result = self.ui.router.route(parsed)
            if result:
                self.ui.add_log(result)
        except Exception as e:
            self.ui.add_log(f"Error: {str(e)}")

    def main(self):
        canvas = urwid.raw_display.Screen()

        left_panel = urwid.ListBox(
            [
                urwid.Text(
                    f"[{self.ui.session_id}] Welcome to E.M.B.E.R v{self.ui.VERSION}"
                )
            ]
        )

        status_sync_about = urwid.Pile(
            [
                urwid.LineBox(StatusBox(self.ui), tl="┌", tr="┐", bl="└", br="┘"),
                urwid.LineBox(SyncBox(self.ui), tl="┌", tr="┐", bl="└", br="┘"),
                urwid.LineBox(AboutBox(self.ui), tl="┌", tr="┐", bl="└", br="┘"),
            ]
        )

        right_panel = urwid.Pile(
            [
                status_sync_about,
                urwid.LineBox(
                    PayloadExplorerBox(self.ui), tl="┌", tr="┐", bl="└", br="┘"
                ),
            ]
        )

        command_panel = urwid.LineBox(
            CommandPromptBox(self.ui), tl="┌", tr="┐", bl="└", br="┘"
        )

        self.command_edit = urwid.Edit("> ", edit_text="")
        urwid.connect_signal(self.command_edit, "postchange", lambda *a: None)

        main_layout = urwid.Pile(
            [
                urwid.Columns(
                    [
                        urwid.LineBox(left_panel, tl="┌", tr="┐", bl="└", br="┘"),
                        right_panel,
                    ]
                ),
                urwid.Columns(
                    [
                        command_panel,
                        self.command_edit,
                    ]
                ),
            ]
        )

        self.loop = urwid.MainLoop(
            main_layout, palette=["header"], screen=canvas, input_filter=self.on_input
        )
        self.loop.run()


def main():
    try:
        app = EMBERApplication()
        app.main()
    except KeyboardInterrupt:
        print("\nExiting E.M.B.E.R...")
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
