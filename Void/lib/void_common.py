"""Void OSINT Toolkit — shared UI helpers."""
import os
import re
import select
import shutil
import sys
import time

from rich.align import Align
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich import box

from . import constants as C
from .config import get_settings

console = Console(highlight=False)


def cls():
    os.system("cls" if os.name == "nt" else "clear")


def tw():
    return shutil.get_terminal_size((100, 30)).columns


def th():
    return shutil.get_terminal_size((100, 30)).lines


def ansi_hex(h):
    hx = h.lstrip("#")
    r, g, b = int(hx[0:2], 16), int(hx[2:4], 16), int(hx[4:6], 16)
    return f"\033[38;2;{r};{g};{b}m"


# ── Cross-platform keyboard ──────────────────────────
# Normalized arrow codes (same as msvcrt):
#   H=up, P=down, K=left, M=right

if os.name == "nt":
    import msvcrt

    def _read_key(timeout=None):
        _ = timeout
        if not msvcrt.kbhit():
            return None
        k = msvcrt.getch()
        if k in (b"\x00", b"\xe0"):
            k2 = msvcrt.getch()
            while msvcrt.kbhit():
                msvcrt.getch()
            return k2
        return k

    def flush_keys():
        while msvcrt.kbhit():
            msvcrt.getch()
else:
    import termios
    import tty

    _cbreak_active = False
    _cbreak_saved = None

    def cbreak_on():
        global _cbreak_active, _cbreak_saved
        if not sys.stdin.isatty() or _cbreak_active:
            return
        fd = sys.stdin.fileno()
        _cbreak_saved = termios.tcgetattr(fd)
        new = termios.tcgetattr(fd)
        new[tty.LFLAG] &= ~(termios.ECHO | termios.ICANON)
        new[tty.IFLAG] &= ~(termios.ICRNL | termios.IGNCR | termios.INLCR)
        new[tty.CC][termios.VMIN] = 1
        new[tty.CC][termios.VTIME] = 0
        termios.tcsetattr(fd, termios.TCSANOW, new)
        _cbreak_active = True

    def cbreak_off():
        global _cbreak_active, _cbreak_saved
        if not _cbreak_active or _cbreak_saved is None:
            return
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, _cbreak_saved)
        _cbreak_active = False
        _cbreak_saved = None

    def _read_key(timeout=None):
        if not sys.stdin.isatty():
            return None
        fd = sys.stdin.fileno()
        if timeout is not None:
            r, _, _ = select.select([fd], [], [], timeout)
            if not r:
                return None
        need_cbreak = not _cbreak_active
        if need_cbreak:
            old = termios.tcgetattr(fd)
            new = termios.tcgetattr(fd)
            new[tty.LFLAG] &= ~(termios.ECHO | termios.ICANON)
            new[tty.IFLAG] &= ~(termios.ICRNL | termios.IGNCR | termios.INLCR)
            new[tty.CC][termios.VMIN] = 1
            new[tty.CC][termios.VTIME] = 0
            termios.tcsetattr(fd, termios.TCSANOW, new)
        try:
            raw = os.read(fd, 1)
            if not raw:
                return None
            ch = raw.decode()
            if ch == "\n":
                return b"\r"
            if ch == "\x1b":
                rest = ""
                for _ in range(2):
                    r2, _, _ = select.select([fd], [], [], 0.15)
                    if r2:
                        rest += os.read(fd, 1).decode()
                    else:
                        break
                seq = "\x1b" + rest
                if len(seq) >= 3:
                    mapping = {"A": b"H", "B": b"P", "C": b"M", "D": b"K"}
                    return mapping.get(seq[2], seq.encode())
                return seq.encode()
            return raw
        finally:
            if need_cbreak:
                termios.tcsetattr(fd, termios.TCSADRAIN, old)

    def flush_keys():
        if not sys.stdin.isatty():
            return
        fd = sys.stdin.fileno()
        need_cbreak = not _cbreak_active
        if need_cbreak:
            old = termios.tcgetattr(fd)
            new = termios.tcgetattr(fd)
            new[tty.LFLAG] &= ~(termios.ECHO | termios.ICANON)
            new[tty.IFLAG] &= ~(termios.ICRNL | termios.IGNCR | termios.INLCR)
            new[tty.CC][termios.VMIN] = 1
            new[tty.CC][termios.VTIME] = 0
            termios.tcsetattr(fd, termios.TCSANOW, new)
        while select.select([fd], [], [], 0)[0]:
            os.read(fd, 1)
        if need_cbreak:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def poll_console_key():
    return _read_key(timeout=0)


def read_console_key():
    return _read_key(timeout=None)


def is_arrow(k):
    return k in (b"H", b"P", b"K", b"M")


def pause(msg=None):
    console.print()
    s = get_settings()
    if msg is None:
        msg = (
            f"\033[38;2;120;0;0m  ► Entrée pour continuer…\033[0m"
            if s.lang == "fr"
            else f"\033[38;2;120;0;0m  ► Press Enter to continue…\033[0m"
        )
    input(msg)


def fmt_label(label: str, max_len: int = 24) -> str:
    clean = re.sub(r"\s*\[(PREMIUM|STAR)\]", "", label, flags=re.I).strip()
    if len(clean) > max_len:
        clean = clean[: max_len - 1] + "…"
    return clean


def is_premium(label: str) -> bool:
    return "[PREMIUM]" in str(label).upper()


def sort_free_first(items):
    if not items:
        return items
    head, normal, tail = [], [], []
    for item in items:
        code = str(item[0]).upper()
        if code == "00":
            head.append(item)
        elif code in ("X", "Q", "41"):
            tail.append(item)
        else:
            normal.append(item)
    ordered = [x for x in normal if not is_premium(x[1])] + [x for x in normal if is_premium(x[1])]
    out, n = [], 1
    for _, label, action in ordered:
        out.append((f"{n:02d}", label, action))
        n += 1
    tail_codes = {str(t[0]).upper() for t in tail}
    tail_sorted = [i for i in items if str(i[0]).upper() in tail_codes]
    return head + out + tail_sorted


def count_free_premium(items):
    free = prem = 0
    for _, label, _ in items:
        if is_premium(label):
            prem += 1
        else:
            free += 1
    return free, prem


def panel(title, desc):
    console.print()
    console.print(Panel(
        Align.center(Text.from_markup(
            f"[{C.C_GOLD} bold]◆ {title}[/]\n[{C.C_DIM}]{desc}[/]"
        )),
        border_style=C.C_BLOOD, box=box.DOUBLE_EDGE, padding=(1, 3),
        width=min(64, tw() - 2),
    ))
    console.print()


def error_box(title: str, message: str, detail: str = None):
    body = Text.from_markup(f"[{C.C_NEON} bold]{message}[/]")
    if detail:
        body.append(Text(f"\n{detail}", style=C.C_DIM))
    console.print(Panel(body, title=f"[bold white]✖ {title}[/]", border_style=C.C_NEON, box=box.HEAVY, padding=(1, 2)))


def success_box(title: str, message: str):
    console.print(Panel(
        Text.from_markup(f"[#88FFAA bold]{message}[/]"),
        title=f"[bold white]✔ {title}[/]", border_style="#88FFAA", box=box.ROUNDED, padding=(0, 2),
    ))


def system_msg(tag, message, color=None):
    if color is None:
        color = C.C_NEON
    console.print(Text.from_markup(f"[{C.C_DIM}][[/][{color} bold]{tag}[/][{C.C_DIM}]][/] {message}"))


def progress_bar(current, total, width=30, label=""):
    pct = current / total if total > 0 else 0
    filled = int(width * pct)
    bar = f"[{C.C_NEON}]{'█' * filled}[/{C.C_DIM}]{'░' * (width - filled)}[/]"
    lbl = f" [{C.C_DIM}]{label}[/]" if label else ""
    console.print(f"\r  [{C.C_GOLD}]{current}/{total}[/] {bar} [{C.C_WHITE}]{int(pct*100)}%[/]{lbl}", end="")


def safe_action(fn, tool_name: str = "Module"):
    try:
        fn()
    except KeyboardInterrupt:
        console.print(f"\n[{C.C_DIM}]  ○ {tool_name} — cancelled[/]")
        time.sleep(0.6)
    except Exception as e:
        error_box("Error", tool_name, f"{type(e).__name__}: {e}")
        time.sleep(2)
