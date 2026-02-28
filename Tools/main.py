#!/usr/bin/env python3
import os
import sys
import socket
import subprocess
import time
import shutil
import platform

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)
CONFIG_DIR = os.path.join(SCRIPT_DIR, ".config")
CONFIG_FILE = os.path.join(CONFIG_DIR, "ps5_config.txt")
LOG_FILE = os.path.join(CONFIG_DIR, "log_server.log")

os.makedirs(CONFIG_DIR, exist_ok=True)

PAYLOAD_SENDER = os.path.join(SCRIPT_DIR, "Y2JB", "payload_sender.py")
LOG_SERVER = os.path.join(SCRIPT_DIR, "Y2JB", "log_server.py")
SETLOGSERVER_JS = os.path.join(BASE_DIR, "payloads", "Y2JB", "setlogserver.js")
PS5_HEURISTIC_JS = os.path.join(BASE_DIR, "payloads", "Main", "PS5_Heuristic.js")
LAPSE_JS = os.path.join(BASE_DIR, "payloads", "Y2JB", "lapse.js")

DEFAULT_PORT = 50000


def get_local_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    return ip


def read_ps5_config():
    if not os.path.exists(CONFIG_FILE):
        return None, None
    with open(CONFIG_FILE, "r") as f:
        lines = f.read().strip().split("\n")
    ip = None
    port = DEFAULT_PORT
    for line in lines:
        if line.startswith("IP:"):
            ip = line.split(":", 1)[1].strip()
        elif line.startswith("PORT:"):
            port = int(line.split(":", 1)[1].strip())
    return ip, port


def write_ps5_config(ip, port):
    with open(CONFIG_FILE, "w") as f:
        f.write(f"IP:{ip}\n")
        f.write(f"PORT:{port}\n")


def ask_ps5_config():
    print("Enter PS5 IP address: ", end="")
    ip = input().strip()
    print("Enter PS5 port (default 50000): ", end="")
    port_input = input().strip()
    port = int(port_input) if port_input else DEFAULT_PORT
    write_ps5_config(ip, port)
    return ip, port


def modify_setlogserver_js(ip):
    with open(SETLOGSERVER_JS, "r") as f:
        content = f.read()

    new_server = f'"http://{ip}:8080/log"'

    import re

    content = re.sub(
        r"LOG_SERVER\s*=\s*[\"'].*?[\"']", f"LOG_SERVER = {new_server}", content
    )

    modified_path = SETLOGSERVER_JS + ".tmp"
    with open(modified_path, "w") as f:
        f.write(content)
    return modified_path


def send_payload(file_path, host, port=DEFAULT_PORT):
    with open(file_path, "rb") as f:
        data = f.read()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    sock.sendall(data)
    sock.close()
    print(f"Sent {len(data)} bytes to {host}:{port}")


def ask_firewall_permission():
    system = platform.system()
    if system == "Linux":
        print("\n[!] You may need to allow incoming traffic on port 8080.")
        print("    Run: sudo ufw allow 8080/tcp")
        response = input("    Allow now? (y/n): ").strip().lower()
        if response == "y":
            subprocess.run(["sudo", "ufw", "allow", "8080/tcp"], check=False)
            print("    Port 8080 allowed.")
    elif system == "Windows":
        print("\n[!] You may need to allow Python through Windows Firewall.")
        print("    Allow python.exe in Windows Firewall when prompted.")
        input("    Press Enter after allowing...")


def wait_for_fw_version(timeout=60):
    print(f"Waiting for FW_VERSION from log server (timeout: {timeout}s)...")
    start = time.time()
    while time.time() - start < timeout:
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                content = f.read()
            if "FW_VERSION:" in content:
                for line in content.split("\n"):
                    if "FW_VERSION:" in line:
                        version_str = line.split("FW_VERSION:", 1)[1].strip()
                        return version_str
        time.sleep(1)
    return None


def parse_fw_version(version_str):
    try:
        parts = version_str.split(".")
        major = int(parts[0])
        minor = int(parts[1]) if len(parts) > 1 else 0
        return major * 100 + minor
    except:
        return 999


def main():
    config_override = "--config" in sys.argv

    print("=== PS5 Jailbreak Toolset ===\n")

    local_ip = get_local_ip()
    print(f"Local IP: {local_ip}")

    print("\nStarting log server in background...")
    with open(LOG_FILE, "w") as logf:
        proc = subprocess.Popen(
            [sys.executable, LOG_SERVER], stdout=logf, stderr=subprocess.STDOUT
        )
    time.sleep(2)
    print(f"Log server running (PID: {proc.pid})")

    if config_override or not os.path.exists(CONFIG_FILE):
        ps5_ip, ps5_port = ask_ps5_config()
    else:
        ps5_ip, ps5_port = read_ps5_config()
    if ps5_ip is None or ps5_port is None:
        ps5_ip, ps5_port = ask_ps5_config()
    else:
        ps5_port = ps5_port if ps5_port else DEFAULT_PORT
        print(f"Using saved PS5 config: {ps5_ip}:{ps5_port}")

    print("\n--- Firewall Notice ---")
    ask_firewall_permission()

    print("\nModifying setlogserver.js...")
    modified_setlogserver = modify_setlogserver_js(local_ip)

    print(f"\nSending setlogserver.js to {ps5_ip}:{ps5_port}...")
    send_payload(modified_setlogserver, ps5_ip, ps5_port)

    print(f"Sending PS5_Heuristic.js to {ps5_ip}:{ps5_port}...")
    send_payload(PS5_HEURISTIC_JS, ps5_ip, ps5_port)

    print("\nWaiting for PS5 to respond with FW_VERSION...")
    fw_version = wait_for_fw_version()

    if fw_version is None:
        print("ERROR: Timeout waiting for FW_VERSION from PS5")
        proc.terminate()
        sys.exit(1)

    print(f"Detected FW_VERSION: {fw_version}")

    fw_num = parse_fw_version(fw_version)
    if fw_num > 1001:
        print("\nlapse.js cannot be run on FW Versions higher than 10.01")
        print("Stopping here.")
        proc.terminate()
        sys.exit(0)

    print(f"\nSending lapse.js to {ps5_ip}:{ps5_port}...")
    send_payload(LAPSE_JS, ps5_ip, ps5_port)

    print("\n=== All payloads sent successfully ===")
    proc.terminate()


if __name__ == "__main__":
    main()
