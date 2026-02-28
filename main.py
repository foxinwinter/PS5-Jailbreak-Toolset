#!/usr/bin/env python3
# main.py
# Copyright (c) 2026 foxinwinter
# Licensed under GPLv3. See Extra/Licenses/LICENSE

import argparse
import sys
import os
import importlib
import inspect

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT_DIR)

from Core.Exploits.Y2JB import Y2JB as Y2JBClass

EXPLOITS = {}
EXPLOIT_INFO = {}


def scan_exploits():
    exploits_dir = os.path.join(ROOT_DIR, "Core", "Exploits")
    info_dir = os.path.join(exploits_dir, "info")

    for filename in os.listdir(exploits_dir):
        if filename.endswith(".py") and not filename.startswith("_"):
            module_name = filename[:-3]
            try:
                module = importlib.import_module(f"Core.Exploits.{module_name}")
                for name, obj in inspect.getmembers(module):
                    if inspect.isclass(obj) and name != "Y2JB" and hasattr(obj, "run"):
                        EXPLOITS[name.upper()] = obj
                        EXPLOIT_INFO[name.upper()] = load_exploit_info(
                            info_dir, module_name
                        )
            except Exception as e:
                print(f"Warning: Failed to load exploit module {module_name}: {e}")

    if not EXPLOITS:
        try:
            EXPLOITS["Y2JB"] = Y2JBClass
            EXPLOIT_INFO["Y2JB"] = load_exploit_info(info_dir, "Y2JB")
        except (AttributeError, NameError):
            pass


def load_exploit_info(info_dir, exploit_name):
    info_file = os.path.join(info_dir, f"{exploit_name}.txt")
    info = {"About": "N/A", "Author": "N/A", "License": "N/A"}

    if os.path.exists(info_file):
        try:
            with open(info_file, "r") as f:
                content = f.read()
                for line in content.strip().split("\n"):
                    line = line.strip()
                    if line.startswith("About:"):
                        info["About"] = line.split(":", 1)[1].strip()
                    elif line.startswith("Author:"):
                        info["Author"] = line.split(":", 1)[1].strip()
                    elif line.startswith("License:"):
                        license_path = line.split(":", 1)[1].strip()
                        license_path = license_path.replace("RepoRoot", ROOT_DIR)
                        info["License"] = license_path
        except Exception:
            pass

    return info


def list_exploits():
    print("\nAvailable Exploits:")
    print(f"{'Name':<20} {'Author':<20} {'About'}")
    print("-" * 70)
    for name, info in EXPLOIT_INFO.items():
        about = info.get("About", "N/A")
        if len(about) > 25:
            about = about[:22] + "..."
        author = info.get("Author", "N/A")
        if len(author) > 18:
            author = author[:15] + "..."
        print(f"{name:<20} {author:<20} {about}")
    print()


def show_exploit_info(exploit_name):
    name = exploit_name.upper()
    if name not in EXPLOIT_INFO:
        print(f"Error: Unknown exploit '{exploit_name}'")
        print(f"Available exploits: {', '.join(EXPLOITS.keys())}")
        sys.exit(1)

    info = EXPLOIT_INFO[name]
    print(f"\n=== {name} ===")
    print(f"About:    {info.get('About', 'N/A')}")
    print(f"Author:   {info.get('Author', 'N/A')}")
    print(f"License:  {info.get('License', 'N/A')}")
    print()


def main():
    scan_exploits()

    parser = argparse.ArgumentParser(
        description="PS5 Jailbreak Toolset",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --exploit Y2JB
  python main.py --exploit Y2JB --config
  python main.py --exploit list
  python main.py --exploit info Y2JB
        """,
    )

    parser.add_argument(
        "--exploit",
        type=str,
        nargs="+",
        help="Exploit to use, or 'list' to list, or 'info <name>' for info",
    )

    parser.add_argument(
        "--config", action="store_true", help="Force prompt for PS5 configuration"
    )

    args = parser.parse_args()

    if not args.exploit:
        parser.print_help()
        sys.exit(1)

    if args.exploit[0].lower() == "list":
        list_exploits()
        sys.exit(0)

    if args.exploit[0].lower() == "info":
        if len(args.exploit) < 2:
            print("Error: Please specify an exploit name")
            print(f"Available exploits: {', '.join(EXPLOITS.keys())}")
            sys.exit(1)
        show_exploit_info(args.exploit[1])
        sys.exit(0)

    exploit_name = args.exploit[0].upper()

    if exploit_name in EXPLOITS:
        exploit = EXPLOITS[exploit_name]()
        exploit.run(config_override=args.config)
    else:
        print(f"Error: Unknown exploit '{args.exploit[0]}'")
        print(f"Available exploits: {', '.join(EXPLOITS.keys())}")
        sys.exit(1)


if __name__ == "__main__":
    main()
