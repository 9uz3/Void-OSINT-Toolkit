"""Main dashboard — Rich layout, live clock, sidebar scroll."""
import shutil
import sys
import time

from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

from . import constants as C
from .config import get_settings
from .pages import build_pages_data
from .search import run_search_ui
from .ui import make_card_cell, make_title_text, monitor_block
from .void_common import cbreak_off, cbreak_on, cls, flush_keys, is_arrow, poll_console_key, safe_action, sort_free_first


class MasterRouter:
    MAX_ROWS = 4
    MAX_CAT_VISIBLE = 9

    def __init__(self):
        self.settings = get_settings()
        cats = [
            ("home", "HOME"), ("email-osint", "EMAIL"), ("phone-osint", "PHONE"),
            ("ip-osint", "IP / NET"), ("username-osint", "USERNAME"),
            ("domain-osint", "DOMAIN"), ("social-osint", "SOCIAL"),
            ("breach-osint", "BREACH"), ("web-osint", "WEB"),
            ("dork-osint", "DORK"), ("image-osint", "IMAGE"),
            ("about", "ABOUT"),
        ]
        self.categories = cats
        self.cat_idx = 0
        self.cat_scroll = 0
        self.grid_idx = 0
        self.scroll_row = 0
        self.focus = "sidebar"
        self.running = True
        self._next_remote = time.time() + 300
        self.pages_data = build_pages_data()
        skip = {"home", "about"}
        for key, items in self.pages_data.items():
            if key not in skip:
                self.pages_data[key] = sort_free_first(items)

    def _cat_key(self):
        return self.categories[self.cat_idx][0]

    def _tools(self):
        return self.pages_data.get(self._cat_key(), [])

    def _sync_cat_scroll(self):
        n = len(self.categories)
        max_scroll = max(0, n - self.MAX_CAT_VISIBLE)
        if self.cat_idx < self.cat_scroll:
            self.cat_scroll = self.cat_idx
        elif self.cat_idx >= self.cat_scroll + self.MAX_CAT_VISIBLE:
            self.cat_scroll = self.cat_idx - self.MAX_CAT_VISIBLE + 1
        self.cat_scroll = max(0, min(self.cat_scroll, max_scroll))

    def _sync_scroll(self):
        tools = self._tools()
        n = len(tools)
        if not n:
            self.scroll_row = 0
            return
        total_rows = (n + 1) // 2
        active_row = self.grid_idx // 2
        max_scroll = max(0, total_rows - self.MAX_ROWS)
        if active_row < self.scroll_row:
            self.scroll_row = active_row
        elif active_row >= self.scroll_row + self.MAX_ROWS:
            self.scroll_row = active_row - self.MAX_ROWS + 1
        self.scroll_row = max(0, min(self.scroll_row, max_scroll))

    def build_ui(self):
        s = self.settings
        tools = self._tools()
        phase = (time.time() * 0.15) % 1.0 if C.is_rainbow() else 0.0
        pal = C.palette(phase)
        n = len(tools)
        if n:
            self.grid_idx = max(0, min(n - 1, self.grid_idx))
        else:
            self.grid_idx = 0
        self._sync_cat_scroll()
        self._sync_scroll()

        layout = Layout()
        layout.split_column(Layout(name="header", size=4), Layout(name="main"))
        layout["main"].split_row(Layout(name="sidebar", size=30), Layout(name="body"))

        head = Table.grid(expand=True)
        head.add_column(ratio=1, justify="left")
        head.add_column(ratio=2, justify="center")
        head.add_column(ratio=1, justify="right")
        head.add_row(
            Text.from_markup(f"[{pal['neon']} bold]● ONLINE[/]"),
            make_title_text("VOID OSINT", phase),
            Text.from_markup(f"[bold {pal['neon']}]{s.username[:16]}[/]"),
        )
        sub = f"[ {time.strftime('%H:%M:%S')} ]"
        layout["header"].update(Panel(
            head, border_style=pal["blood"], box=box.HEAVY_EDGE,
            subtitle=sub,
        ))

        sidebar = Table.grid(expand=True)
        n_cat = len(self.categories)
        cat_up = f"[{pal['neon']}]▲[/]" if self.cat_scroll > 0 else " "
        cat_dn = f"[{pal['neon']}]▼[/]" if self.cat_scroll + self.MAX_CAT_VISIBLE < n_cat else " "
        sidebar.add_row(Text.from_markup(f"[{C.C_DIM}]{cat_up} {cat_dn}[/]"))

        end_cat = min(n_cat, self.cat_scroll + self.MAX_CAT_VISIBLE)
        for i in range(self.cat_scroll, end_cat):
            _, label = self.categories[i]
            act = i == self.cat_idx
            foc = act and self.focus == "sidebar"
            if foc:
                sidebar.add_row(Text.from_markup(f"[black on {pal['neon']} bold] » {label:<22} [/]"))
            elif act:
                sidebar.add_row(Text.from_markup(f"[{pal['neon']} bold] █ {label:<22} [/]"))
            else:
                sidebar.add_row(Text.from_markup(f"[{C.C_DIM}] │ {label:<22} [/]"))

        cat_label = self.categories[self.cat_idx][1]
        layout["sidebar"].update(Panel(
            Group(sidebar, monitor_block(cat_label, n, tools, s.username, phase)),
            title="[bold white]CATEGORIES",
            border_style=pal["mid"],
            box=box.SQUARE,
            padding=(1, 2),
        ))

        start = self.scroll_row * 2
        end = min(n, start + self.MAX_ROWS * 2)
        visible = tools[start:end]
        grid = Table.grid(expand=True, padding=(1, 1))
        grid.add_column(ratio=1)
        grid.add_column(ratio=1)
        for i in range(0, len(visible), 2):
            L = visible[i]
            right = visible[i + 1] if i + 1 < len(visible) else None
            abs_l, abs_r = start + i, start + i + 1
            sel = self.focus == "grid"
            grid.add_row(
                make_card_cell(L[0], L[1], sel and self.grid_idx == abs_l, phase),
                make_card_cell(right[0], right[1], sel and self.grid_idx == abs_r, phase) if right else Text(""),
            )

        total_rows = max(1, (n + 1) // 2)
        up = f"[{pal['neon']}] ▲ MORE UP [/]" if self.scroll_row > 0 else "                  "
        dn = f"[{pal['neon']}] ▼ MORE DOWN [/]" if self.scroll_row + self.MAX_ROWS < total_rows else "                  "
        footer = Text.assemble(
            Text.from_markup(up), Text("   "), Text.from_markup(dn),
            Text("   "), Text.from_markup(f"[{C.C_DIM}]←→ · ↑↓ · Enter · F[/]"),
        )
        layout["body"].update(Panel(
            grid,
            title=f"[bold white]{cat_label}",
            subtitle=footer,
            border_style=pal["blood"],
            box=box.DOUBLE,
            padding=(1, 2),
        ))
        return layout

    def _on_arrow(self, k):
        tools = self._tools()
        n = len(tools)

        if k == b"H":
            if self.focus == "sidebar":
                self.cat_idx = (self.cat_idx - 1) % len(self.categories)
                self.grid_idx = 0
                self.scroll_row = 0
                self._sync_cat_scroll()
            else:
                self.grid_idx = max(0, self.grid_idx - 2)
                self._sync_scroll()
        elif k == b"P":
            if self.focus == "sidebar":
                self.cat_idx = (self.cat_idx + 1) % len(self.categories)
                self.grid_idx = 0
                self.scroll_row = 0
                self._sync_cat_scroll()
            else:
                if n:
                    if self.grid_idx + 2 < n:
                        self.grid_idx += 2
                    elif self.grid_idx + 1 < n:
                        self.grid_idx += 1
                self._sync_scroll()
        elif k == b"K":
            if self.focus == "grid":
                if self.grid_idx % 2 == 0:
                    self.focus = "sidebar"
                else:
                    self.grid_idx -= 1
        elif k == b"M":
            if self.focus == "sidebar":
                self.focus = "grid"
                self.grid_idx = 0
            elif self.grid_idx % 2 == 0 and n:
                self.grid_idx = min(n - 1, self.grid_idx + 1)

    def _on_key(self, k):
        if is_arrow(k):
            self._on_arrow(k)
            return "redraw"

        if k == b"\r":
            flush_keys()
            if self.focus == "grid":
                tools = self._tools()
                if tools and self.grid_idx < len(tools):
                    return ("run", tools[self.grid_idx][2], tools[self.grid_idx][1])
            else:
                self.focus = "grid"
                self.grid_idx = 0
            return "redraw"

        if k in (b"f", b"F"):
            flush_keys()
            return "search"

        if k == b"\x03":
            return "exit"

        return None

    def _run_tool(self, live, action, label="Module"):
        live.stop()
        cls()
        cbreak_off()
        try:
            safe_action(action, label)
        finally:
            cbreak_on()
        cls()
        live.start()
        flush_keys()

    def _run_search(self, live):
        live.stop()
        cls()
        cbreak_off()
        try:
            run_search_ui(self, live)
        finally:
            cbreak_on()
        cls()
        live.start()
        flush_keys()

    def start(self):
        cols, rows = shutil.get_terminal_size((100, 30))
        if cols < 90 or rows < 28:
            cls()
            print(f"\n  [!] Terminal too small ({cols}x{rows}). Min ~100x30.\n")
            input("  Enter...")
        cls()
        sys.stdin.flush()
        flush_keys()
        cbreak_on()
        try:
            with Live(self.build_ui(), auto_refresh=False, screen=True, transient=False) as live:
                next_clock = time.time()
                while self.running:
                    now = time.time()
                    if now >= next_clock:
                        live.update(self.build_ui(), refresh=True)
                        next_clock = now + 1.0

                    k = poll_console_key()
                    if k is None:
                        time.sleep(0.03)
                        continue
                    res = self._on_key(k)
                    if res == "exit":
                        break
                    if isinstance(res, tuple):
                        self._run_tool(live, res[1], res[2])
                    elif res == "search":
                        self._run_search(live)
                    if res:
                        live.update(self.build_ui(), refresh=True)
                        next_clock = time.time() + 1.0
        finally:
            cbreak_off()
