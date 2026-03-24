#!/usr/bin/env python3
# core/command/commands/payload.py
# Handles: send payload, resend last payload - talks to payload_manager


def handle_send_payload(payload_manager, args: list) -> str:
    if not args:
        return "Usage: send <payload-path>"

    payload_path = args[0]
    result = payload_manager.send_payload(payload_path)

    if result:
        return f"Payload sent: {payload_path}"
    return "Failed to send payload."


def handle_resend_payload(payload_manager) -> str:
    last_payload = payload_manager.get_last_payload()
    if not last_payload:
        return "No previous payload to resend."

    result = payload_manager.send_payload(last_payload)
    if result:
        return f"Resent: {last_payload}"
    return "Failed to resend payload."


def handle_list_payloads(payload_manager) -> list:
    return payload_manager.list_available_payloads()


def handle_refresh_payloads(payload_manager) -> str:
    payload_manager.refresh_payload_list()
    return "Payload list refreshed."
