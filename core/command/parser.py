#!/usr/bin/env python3
# core/command/parser.py
# Takes Raw Input, and splits it into: { "command": "command-name", "args": ["", "test.lua"] }


def parse_command(raw_input: str) -> dict:
    if not raw_input or not raw_input.strip():
        return {"command": None, "args": []}

    parts = raw_input.strip().split()
    command = parts[0].lower() if parts else None
    args = parts[1:] if len(parts) > 1 else []

    return {"command": command, "args": args}
