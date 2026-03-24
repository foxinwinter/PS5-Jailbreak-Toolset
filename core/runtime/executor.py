#!/usr/bin/env python3
# core/runtime/executor.py
# Actually runs things: Payload Send, Exploit Execution


import os


class Executor:
    def __init__(
        self,
        session_manager,
        device_manager,
        payload_manager,
        exploit_manager,
        log_manager,
    ):
        self.session_manager = session_manager
        self.device_manager = device_manager
        self.payload_manager = payload_manager
        self.exploit_manager = exploit_manager
        self.log_manager = log_manager

    def execute_send_payload(self, payload_path: str) -> str:
        if not self.session_manager.get_selected_exploit():
            return "No exploit selected. Use 'select' command first."

        if not self.session_manager.get_target_info().get("ip"):
            return "No target configured. Use 'config' command first."

        allow_unsafe = self.payload_manager.validate_payload(
            payload_path, allow_unsafe=True
        )
        safe = self.payload_manager.validate_payload(payload_path, allow_unsafe=False)

        if not safe and not allow_unsafe:
            return "Payload not compatible with selected exploit."

        result = self.payload_manager.send_payload(payload_path, self.device_manager)

        if result:
            self.log_manager.write_log(
                self.session_manager.get_session_id() or "N/A",
                f"Sent payload: {payload_path}",
            )
            return f"Payload sent: {payload_path}"
        return "Failed to send payload."

    def execute_resend_last(self) -> str:
        last = self.payload_manager.get_last_payload()
        if not last:
            return "No previous payload."
        return self.execute_send_payload(last)

    def execute_exploit(self, exploit_name: str) -> str:
        exploit = self.exploit_manager.get_exploit(exploit_name)
        if not exploit:
            return f"Exploit '{exploit_name}' not found."

        self.session_manager.set_selected_exploit(exploit_name)

        handler_path = os.path.join(exploit["path"], "handler.py")
        if os.path.exists(handler_path):
            return f"Loading exploit handler: {handler_path}"

        return f"Exploit {exploit_name} selected."

    def execute_start_logserver(self) -> str:
        result = self.log_manager.start_logserver()
        if result:
            return f"Logserver started (PID: {self.log_manager.get_logserver_pid()})"
        return "Logserver already running."

    def execute_stop_logserver(self) -> str:
        result = self.log_manager.stop_logserver()
        if result:
            return "Logserver stopped."
        return "No logserver to stop."
