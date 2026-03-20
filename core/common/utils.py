import os
import re
import hashlib

ESCAPE_SEQUENCE_RE = re.compile(r"\x1b\[[0-9;]*[a-zA-Z]")


def log_info(msg):
    print(f"[INFO] {msg}")


def log_error(msg):
    print(f"[ERROR] {msg}")


def log_warn(msg):
    print(f"[WARN] {msg}")


def log_ok(msg):
    print(f"[ OK ] {msg}")


def read_file(path):
    with open(path, "r") as f:
        return f.read()


def read_file_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def write_file(path, data):
    with open(path, "w") as f:
        f.write(data)


def ensure_dir(path):
    os.makedirs(path, exist_ok=True)


def sanitize_log(message):
    return ESCAPE_SEQUENCE_RE.sub("", message)


def sha256_file(file_path):
    h = hashlib.sha256()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            h.update(chunk)
    return h.hexdigest()
