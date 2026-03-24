#!/usr/bin/env python3
# core/command/router.py
# Receives parsed command (from parser.py) and decides what handler to call


def route_command(parsed: dict, app_state: dict) -> None:
    command = parsed.get("command")
    args = parsed.get("args", [])

    handlers = {
        "send": "handle_send",
        "start": "handle_start",
        "stop": "handle_stop",
        "clear": "handle_clear",
        "kill": "handle_kill",
        "reconnect": "handle_reconnect",
        "refetch": "handle_refetch",
        "list": "handle_list",
        "select": "handle_select",
        "help": "handle_help",
        "exit": "handle_exit",
        "quit": "handle_quit",
        "debug": "handle_debug",
        "resend": "handle_resend",
        "refresh": "handle_refresh",
        "unsafe": "handle_unsafe",
        "config": "handle_config",
    }

    if command in handlers:
        handler_name = handlers[command]
        return handler_name, args

    return None, args
