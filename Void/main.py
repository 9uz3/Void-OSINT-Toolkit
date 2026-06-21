#!/usr/bin/env python3
"""Void OSINT Toolkit — v1.1 · Standalone OSINT toolkit"""
import os
import subprocess
import sys

_VOID = os.path.dirname(os.path.abspath(__file__))
if _VOID not in sys.path:
    sys.path.insert(0, _VOID)

_REQUIREMENTS = [
    "rich>=13.0.0", "colorama>=0.4.6", "requests>=2.28.0",
    "beautifulsoup4>=4.12.0", "phonenumbers>=8.13.0",
    "dnspython>=2.3.0", "Pillow>=10.0.0",
]


def _auto_install():
    try:
        import rich, colorama, requests, bs4, phonenumbers, dns, PIL
        return
    except ImportError:
        pass

    req_path = os.path.join(_VOID, "requirements.txt")
    target = ["-r", req_path] if os.path.isfile(req_path) else _REQUIREMENTS
    print("[*] Installing Void OSINT dependencies...")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-q"] + target
        )
        print("[+] Dependencies installed.")
    except Exception as e:
        print(f"[!] Auto-install failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("-")]

    if args and args[0] in ("doctor", "update", "modules"):
        from lib.deps import run_deps_command
        run_deps_command(args)
    else:
        _auto_install()
        from lib.entry import run_void
        run_void()
