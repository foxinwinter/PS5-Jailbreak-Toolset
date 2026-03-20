import os
import json


def verify_hash(expected, actual):
    return expected == actual


def is_payload_trusted(name, trusted_hashes, actual_hash):
    return trusted_hashes.get(name) == actual_hash


def load_trusted_hashes_from_file(hashes_file):
    trusted = {}
    if not os.path.exists(hashes_file):
        return trusted
    with open(hashes_file, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                name, hash_val = line.split(":", 1)
                name = name.strip().upper()
                hash_val = hash_val.strip()
                trusted[name] = hash_val
    return trusted


def check_file_integrity(file_path, trusted_hashes, hash_name):
    if not os.path.exists(file_path):
        return False, "File not found"
    actual_hash = None
    with open(file_path, "rb") as f:
        import hashlib

        h = hashlib.sha256()
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
        actual_hash = h.hexdigest()
    if hash_name in trusted_hashes:
        expected_hash = trusted_hashes[hash_name]
        if actual_hash == expected_hash:
            return True, actual_hash
        return False, actual_hash
    return None, actual_hash


def sanitize_for_display(message, max_length=200):
    import re

    escape_re = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")
    sanitized = escape_re.sub("", message)
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
    return sanitized


def validate_ip(ip):
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
        except ValueError:
            return False
    return True


def validate_port(port):
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False


def is_safe_filename(filename):
    import re

    safe_pattern = re.compile(r"^[a-zA-Z0-9_\-\.]+$")
    return bool(safe_pattern.match(filename))
