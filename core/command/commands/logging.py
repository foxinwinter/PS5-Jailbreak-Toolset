#!/usr/bin/env python3
# core/command/commands/logging.py
# Handles: start logserver, stop logserver, clear logs - talks to log_manager


def handle_start_logserver(log_manager) -> str:
    result = log_manager.start_logserver()
    if result:
        pid = log_manager.get_logserver_pid()
        return f"Logserver started (PID: {pid})"
    return "Failed to start logserver."


def handle_stop_logserver(log_manager) -> str:
    result = log_manager.stop_logserver()
    if result:
        return "Logserver stopped."
    return "No logserver running."


def handle_clear_logs(log_manager) -> str:
    log_manager.clear_logs()
    return "Logs cleared."


def handle_pause_logs(log_manager) -> str:
    log_manager.pause_logs()
    return "Logs paused."


def handle_resume_logs(log_manager) -> str:
    log_manager.resume_logs()
    return "Logs resumed."
