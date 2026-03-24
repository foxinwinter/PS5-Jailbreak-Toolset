#!/usr/bin/env python3
# core/command/commands/system.py
# Handles: refetch target info, debug mode - talks to many managers


def handle_refetch_target(device_manager, session_manager) -> dict:
    target = session_manager.get_target_info()
    if not target:
        return {"error": "No target configured"}

    info = device_manager.get_device_info(target["ip"], target["port"])
    return info


def handle_enable_debug(app_state: dict) -> str:
    app_state["debug_mode"] = True
    return "Debug mode enabled."


def handle_disable_debug(app_state: dict) -> str:
    app_state["debug_mode"] = False
    return "Debug mode disabled."


def handle_enable_unsafe(app_state: dict) -> str:
    app_state["allow_unsafe_payloads"] = True
    return "Unsafe payload mode enabled."


def handle_get_system_info(app_state: dict) -> dict:
    return {
        "version": app_state.get("version", "1.0.0"),
        "build": app_state.get("build", "dev"),
        "debug_mode": app_state.get("debug_mode", False),
        "unsafe_mode": app_state.get("allow_unsafe_payloads", False),
    }
