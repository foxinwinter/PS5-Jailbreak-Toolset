#!/usr/bin/env python3
# core/managers/log_manager.py
# Writes logs to logs/active/latest.log, handles logserver.pid file


import os
import time
import signal


class LogManager:
    def __init__(self):
        self.logserver_pid = None
        self.logs_paused = False
        self.log_file = None
        self._init_directories()

    def _init_directories(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.logs_dir = os.path.join(base_dir, "logs")
        self.active_dir = os.path.join(self.logs_dir, "active")
        self.sessions_dir = os.path.join(self.logs_dir, "sessions")
        self.errors_dir = os.path.join(self.logs_dir, "errors")

        for d in [self.active_dir, self.sessions_dir, self.errors_dir]:
            os.makedirs(d, exist_ok=True)

        self.latest_log = os.path.join(self.active_dir, "latest.log")
        self.pid_file = os.path.join(self.active_dir, "logserver.pid")

    def _load_pid(self):
        if os.path.exists(self.pid_file):
            try:
                with open(self.pid_file, "r") as f:
                    return int(f.read().strip())
            except:
                return None
        return None

    def start_logserver(self) -> bool:
        self.logserver_pid = self._load_pid()
        if self.logserver_pid:
            try:
                os.kill(self.logserver_pid, 0)
                return False
            except OSError:
                pass

        import subprocess

        logserver_script = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            "exploits",
            "shared",
            "logserver.py",
        )

        if os.path.exists(logserver_script):
            try:
                proc = subprocess.Popen(
                    ["python3", logserver_script],
                    stdout=open(self.latest_log, "a"),
                    stderr=subprocess.STDOUT,
                )
                with open(self.pid_file, "w") as f:
                    f.write(str(proc.pid))
                self.logserver_pid = proc.pid
                return True
            except:
                pass
        return False

    def stop_logserver(self) -> bool:
        pid = self._load_pid()
        if pid:
            try:
                os.kill(pid, signal.SIGTERM)
                if os.path.exists(self.pid_file):
                    os.remove(self.pid_file)
                self.logserver_pid = None
                return True
            except:
                pass
        return False

    def get_logserver_pid(self) -> str:
        pid = self._load_pid()
        if pid:
            return str(pid)
        return "Not running"

    def write_log(self, session_id: str, message: str):
        if self.logs_paused:
            return
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] [{session_id}] {message}\n"

        with open(self.latest_log, "a") as f:
            f.write(log_line)

    def clear_logs(self):
        if os.path.exists(self.latest_log):
            os.remove(self.latest_log)

    def pause_logs(self):
        self.logs_paused = True

    def resume_logs(self):
        self.logs_paused = False
