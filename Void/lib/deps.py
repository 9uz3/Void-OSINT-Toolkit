"""Dependency manager — doctor, update, modules commands."""
import importlib
import os
import platform
import subprocess
import sys

from rich.table import Table
from rich.text import Text
from rich.padding import Padding
from rich.panel import Panel
from rich.align import Align
from rich import box

from . import constants as C
from .void_common import ansi_hex as _a, console

_VOID_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_REQ_FILE = os.path.join(_VOID_DIR, "requirements.txt")

CORE_PACKAGES = [
    "colorama", "rich", "requests", "dns", "bs4",
    "phonenumbers", "PIL", "aiohttp",
]

CORE_NAMES = {
    "colorama": "colorama",
    "rich": "rich",
    "requests": "requests",
    "dns": "dnspython",
    "bs4": "beautifulsoup4",
    "phonenumbers": "phonenumbers",
    "PIL": "Pillow",
    "aiohttp": "aiohttp",
}

SCANNER_PACKAGES = [
    "user_scanner",
]


def _check_import(mod_name):
    try:
        mod = importlib.import_module(mod_name)
        ver = getattr(mod, "__version__", None)
        if ver:
            return True, ver
        if mod_name == "PIL":
            from PIL import __version__ as pil_ver
            return True, pil_ver
        return True, "✓"
    except ImportError:
        return False, None


def _pip_list():
    try:
        r = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=columns"],
            capture_output=True, text=True, timeout=15
        )
        return r.stdout
    except Exception:
        return ""


def cmd_doctor():
    console.print()
    console.print(Text.from_markup(
        f"[{C.C_BLOOD}]╔{'═'*58}╗[/]\n"
        f"[{C.C_BLOOD}]║[/]  [{C.C_NEON}]VOID DOCTOR[/]  [{C.C_DIM}]System diagnostics[/]{' '*(23)}[{C.C_BLOOD}]║[/]\n"
        f"[{C.C_BLOOD}]╚{'═'*58}╝[/]"
    ))

    console.print()

    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C.C_BLOOD, show_header=True)
    table.add_column("Check", style=C.C_GOLD, width=24)
    table.add_column("Status", width=36)

    py_ver = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    table.add_row("Python", py_ver)
    table.add_row("Platform", platform.platform())
    table.add_row("Void root", _VOID_DIR)

    ok_pkg = 0
    fail_pkg = 0
    for mod in CORE_PACKAGES:
        ok, ver = _check_import(mod)
        pkg_name = CORE_NAMES.get(mod, mod)
        if ok:
            ok_pkg += 1
            table.add_row(
                f"  {pkg_name}",
                f"[{C.C_NEON}]✔ {ver}[/]"
            )
        else:
            fail_pkg += 1
            table.add_row(
                f"  {pkg_name}",
                f"[{C.C_BLOOD}]✗ not installed[/]"
            )

    for mod in SCANNER_PACKAGES:
        ok, ver = _check_import(mod)
        if ok:
            ok_pkg += 1
            table.add_row(
                f"  {mod}",
                f"[{C.C_NEON}]✔ {ver or '✓'}[/]"
            )
        else:
            fail_pkg += 1
            table.add_row(
                f"  {mod}",
                f"[{C.C_BLOOD}]✗ not installed[/]"
            )

    console.print(Padding(table, (0, 2)))

    if fail_pkg == 0:
        console.print(Text.from_markup(
            f"\n  [{C.C_NEON}]✔ All dependencies satisfied.[/]"
        ))
    else:
        console.print(Text.from_markup(
            f"\n  [{C.C_BLOOD}]✗ {fail_pkg} missing.[/]  [{C.C_SILVER}]Run:[/] [{C.C_MID}]voidosint update[/]"
        ))


def cmd_update():
    console.print()
    console.print(Text.from_markup(
        f"[{C.C_BLOOD}]╔{'═'*58}╗[/]\n"
        f"[{C.C_BLOOD}]║[/]  [{C.C_NEON}]VOID UPDATE[/]  [{C.C_DIM}]Installing dependencies[/]{' '*(18)}[{C.C_BLOOD}]║[/]\n"
        f"[{C.C_BLOOD}]╚{'═'*58}╝[/]"
    ))

    targets = []

    if os.path.isfile(_REQ_FILE):
        targets.append(_REQ_FILE)

    targets.append("user-scanner")

    for t in targets:
        console.print(Text.from_markup(
            f"  [{C.C_SILVER}]Installing:[/] [{C.C_WHITE}]{t}[/]"
        ))
        try:
            if t == "user-scanner":
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--quiet", "--break-system-packages", t],
                    timeout=120
                )
            else:
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--quiet", "-r", t],
                    timeout=120
                )
            console.print(Text.from_markup(
                f"  [{C.C_NEON}]✔ Done[/]"
            ))
        except subprocess.TimeoutExpired:
            console.print(Text.from_markup(
                f"  [{C.C_BLOOD}]✗ Timeout[/]"
            ))
        except subprocess.CalledProcessError as e:
            if "--break-system-packages" not in t:
                try:
                    subprocess.check_call(
                        [sys.executable, "-m", "pip", "install", "--quiet", "--break-system-packages", "-r", t],
                        timeout=120
                    )
                    console.print(Text.from_markup(
                        f"  [{C.C_NEON}]✔ Done (--break-system-packages)[/]"
                    ))
                    continue
                except Exception:
                    pass
            console.print(Text.from_markup(
                f"  [{C.C_BLOOD}]✗ Failed: {e}[/]"
            ))

    console.print()
    console.print(Text.from_markup(
        f"  [{C.C_NEON}]✔ Update complete[/]"
    ))


def cmd_modules():
    console.print()
    console.print(Text.from_markup(
        f"[{C.C_BLOOD}]╔{'═'*58}╗[/]\n"
        f"[{C.C_BLOOD}]║[/]  [{C.C_NEON}]VOID MODULES[/]  [{C.C_DIM}]Available OSINT modules[/]{' '*(17)}[{C.C_BLOOD}]║[/]\n"
        f"[{C.C_BLOOD}]╚{'═'*58}╝[/]"
    ))

    modules_info = [
        ("Email Intelligence", "user-scanner (90 sites)", True),
        ("Username Intelligence", "user-scanner (182 sites)", True),
        ("Phone Intelligence", "phonenumbers lib", False),
    ]

    scanner_ok, _ = _check_import("user_scanner")
    phone_ok, _ = _check_import("phonenumbers")

    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C.C_BLOOD, show_header=True)
    table.add_column("Module", style=C.C_GOLD, width=24)
    table.add_column("Coverage", style=C.C_SILVER, width=28)
    table.add_column("Status", width=8)

    for name, coverage, needs_scanner in modules_info:
        if needs_scanner and not scanner_ok:
            status = f"[{C.C_BLOOD}]✗[/]"
        elif not needs_scanner and not phone_ok:
            status = f"[{C.C_BLOOD}]✗[/]"
        else:
            status = f"[{C.C_NEON}]✔[/]"
        table.add_row(name, coverage, status)

    console.print(Padding(table, (0, 2)))

    if not scanner_ok:
        console.print(Text.from_markup(
            f"\n  [{C.C_DIM}]  user-scanner not installed.[/]  [{C.C_MID}]Run: voidosint update[/]"
        ))


def run_deps_command(args):
    if not args:
        cmd_doctor()
        return

    cmd = args[0].lower()
    if cmd in ("doctor", "check", "diagnose"):
        cmd_doctor()
    elif cmd in ("update", "install", "upgrade"):
        cmd_update()
    elif cmd in ("modules", "mods", "list"):
        cmd_modules()
    else:
        console.print(Text.from_markup(
            f"  [{C.C_BLOOD}]Unknown command: {cmd}[/]"
        ))
        console.print(Text.from_markup(
            f"  [{C.C_SILVER}]Usage: voidosint [doctor|update|modules][/]"
        ))
