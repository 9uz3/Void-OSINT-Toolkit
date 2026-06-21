"""Unified tool runner — stub for compatibility."""
from .void_common import error_box, pause


def run(folder, fr_name="fr.py", en_name="en.py", tool_name=None):
    error_box("Not implemented", f"External tool: {folder}/{fr_name}",
              "This OSINT toolkit uses built-in tools only.")
    pause()
