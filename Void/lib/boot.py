"""Cinematic boot sequence — Enhanced visual effects."""
import os, select, sys, time, shutil, math, random

from . import constants as C

LOGO_RAW = r"""
╔══════════════════════════════════════════════════════════════════╗
║██╗   ██╗ ██████╗ ██╗██████╗     ██████╗ ███████╗██╗███╗   ██╗████████╗║
║██║   ██║██╔═══██╗██║██╔══██╗   ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝║
║██║   ██║██║   ██║██║██║  ██║   ██║   ██║███████╗██║██╔██╗ ██║   ██║   ║
║╚██╗ ██╔╝██║   ██║██║██║  ██║   ██║   ██║╚════██║██║██║╚██╗██║   ██║   ║
║ ╚████╔╝ ╚██████╔╝██║██████╔╝   ╚██████╔╝███████║██║██║ ╚████║   ██║   ║
║  ╚═══╝   ╚═════╝ ╚═╝╚═════╝     ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   ║
╚══════════════════════════════════════════════════════════════════╝
╔══════════════════════════════════════════════════════════════════╗
║ ████████╗ ██████╗  ██████╗ ██╗     ██╗  ██╗██╗████████╗         ║
║ ╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║ ██╔╝██║╚══██╔══╝         ║
║    ██║   ██║   ██║██║   ██║██║     █████╔╝ ██║   ██║            ║
║    ██║   ██║   ██║██║   ██║██║     ██╔═██╗ ██║   ██║            ║
║    ██║   ╚██████╔╝╚██████╔╝███████╗██║  ██╗██║   ██║            ║
║    ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝╚═╝   ╚═╝            ║
╚══════════════════════════════════════════════════════════════════╝
""".strip("\n")

_RAIN_CHARS = list("01▓▒░│┤╣║╗╝┐└┴┬├─┼╚╔╩╦╠═╬┘┌#%&?$@!")
_GLITCH_CHARS = list("▓▒░█▀▄■□◆◇▲△▼▽◉○●◎⊕⊗⊙")


def _ansi_rgb(r, g, b):
    return f"\033[38;2;{r};{g};{b}m"


def _ansi_reset():
    return "\033[0m"


def _ansi_goto(row, col):
    return f"\033[{row};{col}H"


def _ansi_hide_cursor():
    return "\033[?25l"


def _ansi_show_cursor():
    return "\033[?25h"


def _ansi_clear():
    return "\033[2J\033[H"


def _write(s):
    sys.stdout.write(s)
    sys.stdout.flush()


def _pulse_theme(t, offset=0.0):
    l = 0.60 + 0.30 * math.sin(t * 3.0 + offset)
    v = int(l * 255)
    return v, v, v


def check_skip_boot():
    if os.name == "nt":
        try:
            import msvcrt
            if msvcrt.kbhit():
                msvcrt.getch()
                return True
        except ImportError:
            pass
    else:
        if select.select([sys.stdin], [], [], 0)[0]:
            try:
                sys.stdin.read(1)
                return True
            except Exception:
                pass
    return False


def _phase_vector_scan(tw, th, duration=1.8):
    cx, cy = tw // 2, th // 2
    t0 = time.time()
    while time.time() - t0 < duration:
        if check_skip_boot():
            return
        t = time.time() - t0
        buf = [_ansi_hide_cursor()]
        for i in range(3):
            size_raw = (1 - (t + i * 0.3) % 1.0) * max(tw, th)
            sw, sh = int(size_raw * 1.5), int(size_raw * 0.5)
            r_top, r_bot = cy - sh, cy + sh
            r_left, r_right = cx - sw, cx + sw
            color = _ansi_rgb(200, 200, 200)
            for r, c, sym in [(r_top, r_left, "╔"), (r_top, r_right, "╗"),
                              (r_bot, r_left, "╚"), (r_bot, r_right, "╝")]:
                if 1 <= r <= th and 1 <= c <= tw:
                    buf.append(f"{_ansi_goto(r, c)}{color}{sym}")
            if 1 <= r_top <= th:
                for x in range(max(1, r_left + 1), min(tw, r_right)):
                    buf.append(f"{_ansi_goto(r_top, x)}{color}\u2550")
            if 1 <= r_bot <= th:
                for x in range(max(1, r_left + 1), min(tw, r_right)):
                    buf.append(f"{_ansi_goto(r_bot, x)}{color}\u2550")
        _write("".join(buf))
        time.sleep(0.04)
    _write(_ansi_clear())


def _phase_vector_build(tw, th, logo_lines):
    lh, lw = len(logo_lines), max(len(l) for l in logo_lines)
    lt, ll = (th - lh) // 2, (tw - lw) // 2
    for r, line in enumerate(logo_lines):
        if check_skip_boot():
            break
        row = lt + r
        if row < 1 or row > th:
            continue
        bar = _ansi_rgb(255, 255, 255) + "\u2588" * tw
        _write(f"{_ansi_goto(row, 1)}{bar}")
        time.sleep(0.015)
        colored = f"{_ansi_rgb(180, 180, 180)}{line}"
        _write(f"{_ansi_goto(row, 1)}{' ' * tw}")
        _write(f"{_ansi_goto(row, ll)}{colored}")
        time.sleep(0.01)


def _phase_vector_idle(tw, th, logo_lines):
    lh, lw = len(logo_lines), max(len(l) for l in logo_lines)
    lt, ll = (th - lh) // 2, (tw - lw) // 2
    t0 = time.time()
    while True:
        try:
            import msvcrt
            if msvcrt.kbhit():
                k = msvcrt.getch()
                if k == b'\r':
                    return
        except ImportError:
            import select
            if select.select([sys.stdin], [], [], 0)[0]:
                if sys.stdin.read(1) == '\n':
                    return
        t = time.time() - t0
        buf = [_ansi_hide_cursor()]
        sweep_x = int((t * 40) % (tw + 10))
        for r, line in enumerate(logo_lines):
            row = lt + r
            if row < 1 or row > th:
                continue
            colored = ""
            for c, char in enumerate(line):
                if char == " ":
                    colored += " "
                    continue
                abs_c = ll + c
                if abs_c == sweep_x:
                    colored += f"{_ansi_rgb(255, 255, 255)}{char}"
                elif abs_c == sweep_x - 1 or abs_c == sweep_x + 1:
                    colored += f"{_ansi_rgb(180, 180, 180)}{char}"
                else:
                    colored += f"{_ansi_rgb(100, 100, 100)}{char}"
            buf.append(f"{_ansi_goto(row, ll)}{colored}")
        br_c = _ansi_rgb(120, 120, 120)
        buf.append(f"{_ansi_goto(lt - 2, ll - 4)}{br_c}\u250c\u2500[ VOID OSINT ]\u2500\u2510")
        buf.append(f"{_ansi_goto(lt + lh + 1, ll - 4)}{br_c}\u2514\u2500" + "\u2500" * (lw + 5) + "\u2518")
        prompt = "[ PRESS ENTER TO ACCESS THE VOID ]"
        p_row = lt + lh + 3
        buf.append(f"{_ansi_goto(p_row, (tw - len(prompt)) // 2)}\033[1m{_ansi_rgb(180, 180, 180)}{prompt}\033[0m")
        _write("".join(buf))
        time.sleep(0.016)


def _cinematic_boot():
    logo_lines = LOGO_RAW.split("\n")
    tw, th = shutil.get_terminal_size((120, 35))
    _write(_ansi_clear())
    _write(_ansi_hide_cursor())
    try:
        _phase_vector_scan(tw, th, duration=1.8)
        _phase_vector_build(tw, th, logo_lines)
        _phase_vector_idle(tw, th, logo_lines)
    except Exception:
        pass
    finally:
        _write(_ansi_show_cursor() + _ansi_reset() + _ansi_clear())


def boot(skip_anim=False):
    if not skip_anim:
        _cinematic_boot()
