#!/usr/bin/env python3
# core/utils/file_utils.py


import os
import shutil


def ensure_dir(path: str):
    os.makedirs(path, exist_ok=True)


def read_file(path: str) -> str:
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read()
    return ""


def write_file(path: str, content: str):
    ensure_dir(os.path.dirname(path))
    with open(path, "w") as f:
        f.write(content)


def file_exists(path: str) -> bool:
    return os.path.exists(path)


def list_files(directory: str, extension: str = None) -> list:
    if not os.path.isdir(directory):
        return []
    files = []
    for f in os.listdir(directory):
        if extension is None or f.endswith(extension):
            files.append(f)
    return files


def get_file_size(path: str) -> int:
    if os.path.exists(path):
        return os.path.getsize(path)
    return 0
