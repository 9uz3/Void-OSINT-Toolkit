"""Void OSINT Toolkit entry point."""
import os
import sys

_VOID = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _VOID not in sys.path:
    sys.path.insert(0, _VOID)

from colorama import init
init(autoreset=True)

from lib import constants as C
from lib.boot import boot
from lib.config import get_settings
from lib.router import MasterRouter
from lib.void_common import cls, console, error_box


def run_void():
    s = get_settings()
    C.apply_theme(s.get("theme", "white"))

    if os.name == "nt":
        os.system(f"title VOID OSINT TOOLKIT — {s.username}")

    boot(skip_anim=bool(s.get("skip_boot")))
    cls()
    MasterRouter().start()


if __name__ == "__main__":
    try:
        run_void()
    except KeyboardInterrupt:
        console.print(f"\n[{C.C_DIM}]  ○ Clean exit.[/]")
        sys.exit(0)
    except Exception as e:
        cls()
        error_box("Fatal crash", "Void OSINT Toolkit", f"{type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
