#!/usr/bin/env python3
# core/command/commands/session.py
# Handles: Kill Session, Reconnect - talks to session_manager


def handle_kill_session(session_manager) -> str:
    return session_manager.kill_session()


def handle_reconnect(session_manager, device_manager) -> str:
    session_id = session_manager.get_session_id()
    if not session_id:
        return "No active session to reconnect."

    target = session_manager.get_target_info()
    if not target:
        return "No target configured. Use 'config' command first."

    result = device_manager.connect(target["ip"], target["port"])
    if result:
        return f"Reconnected to {target['ip']}:{target['port']}"
    return "Failed to reconnect."


def handle_session_info(session_manager) -> dict:
    return {
        "session_id": session_manager.get_session_id(),
        "uptime": session_manager.get_uptime(),
        "connection_time": session_manager.get_connection_time(),
    }
