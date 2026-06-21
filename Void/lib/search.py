"""Fuzzy search UI for tools."""
import time

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from . import constants as C
from .void_common import cls, console, poll_console_key, read_console_key, safe_action


def run_search_ui(router, live):
    live.stop()
    cls()

    query = ""
    results = []
    selected = 0

    while True:
        cls()
        console.print(Panel(
            Text.from_markup(
                f"[bold {C.C_NEON}]FUZZY SEARCH[/]\n"
                f"[{C.C_DIM}]Type to filter · Enter to launch · Esc to cancel[/]"
            ),
            border_style=C.C_BLOOD, box=box.DOUBLE_EDGE, padding=(1, 2),
        ))

        console.print(f"\n  [{C.C_NEON}]»[/] [bold white]{query}▌[/]\n")

        if query:
            query_lower = query.lower()
            results = []
            for cat_key, items in router.pages_data.items():
                for code, label, action in items:
                    if query_lower in label.lower() or query_lower in code:
                        results.append((cat_key, code, label, action))
            results = results[:20]

            if results:
                selected = max(0, min(selected, len(results) - 1))
                table = Table(box=box.MINIMAL, border_style=C.C_BLOOD, show_header=False)
                table.add_column("")
                table.add_column("Cat", style=C.C_DIM, width=12)
                table.add_column("#", style=C.C_DIM, width=4)
                table.add_column("Tool", style=C.C_WHITE)
                for i, (ck, cd, lb, _) in enumerate(results):
                    arrow = "[bold #88FFAA]►[/]" if i == selected else "  "
                    table.add_row(arrow, ck.upper(), cd, lb)
                console.print(table)
            else:
                console.print(f"  [{C.C_DIM}]No results found[/]")

        k = poll_console_key()

        if k is None:
            time.sleep(0.05)
            continue

        if k in (b"H", b"P"):
            if results:
                selected = (selected + (-1 if k == b"H" else 1)) % len(results)
        elif k == b"\r":
            if results and selected < len(results):
                _, _, label, action = results[selected]
                cls()
                safe_action(action, label)
                cls()
                input(f"\033[38;2;120;0;0m  ► Enter to return...\033[0m")
            break
        elif k == b"\x1b" or k == b"\x03":
            break
        elif k == b"\x08":
            query = query[:-1]
            selected = 0
        elif len(k) == 1 and k >= b" " and k <= b"~":
            query += k.decode("utf-8", errors="ignore")
            selected = 0

    live.start()
