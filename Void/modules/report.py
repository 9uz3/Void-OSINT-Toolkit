"""Report generation — single TXT file + terminal display."""
import os
from datetime import datetime

from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.padding import Padding
from rich import box

from lib import constants as C
from lib.void_common import console


def show_results_panel(engine):
    now = datetime.now()

    console.print()
    console.print(Text.from_markup(
        f"[{C.C_BLOOD}]╔{'═' * 56}╗[/]\n"
        f"[{C.C_BLOOD}]║[/]  [{C.C_NEON}]INVESTIGATION RESULT[/]{' ' * 34}[{C.C_BLOOD}]║[/]\n"
        f"[{C.C_BLOOD}]╚{'═' * 56}╝[/]"
    ))
    console.print()
    console.print(Text.from_markup(f"  [{C.C_GOLD}]TARGET:[/]   [{C.C_WHITE}]{engine.target}[/]"))
    console.print(Text.from_markup(f"  [{C.C_GOLD}]TYPE:[/]     [{C.C_WHITE}]{engine.scan_type.upper()} INTELLIGENCE[/]"))
    console.print(Text.from_markup(f"  [{C.C_GOLD}]DATE:[/]     [{C.C_WHITE}]{now.strftime('%d/%m/%Y')}[/]"))
    console.print(Text.from_markup(f"  [{C.C_GOLD}]TIME:[/]     [{C.C_WHITE}]{now.strftime('%H:%M:%S')}[/]"))
    console.print(Text.from_markup(f"  [{C.C_GOLD}]STATUS:[/]   [#88FFAA bold]COMPLETED[/]"))
    console.print()

    for r in engine.results:
        if not r.is_success():
            continue
        console.print(Text.from_markup(f"  [{C.C_NEON}]✔[/] [{C.C_GOLD}]{r.source}[/] found:"))
        for k, v in r.data.items():
            v_str = str(v)
            if v_str in ("none", "none found", "N/A", "Unknown", "", "0", "False"):
                continue
            if k == "dorks":
                for dork in v_str.split(" | "):
                    console.print(f"    [{C.C_NEON}]→[/] [{C.C_SILVER}]{dork}[/]")
            elif k in ("associated_accounts", "sites", "breach_names", "profiles"):
                for item in v_str.split(", "):
                    if item and item.strip():
                        console.print(f"    [{C.C_NEON}]→[/] [{C.C_SILVER}]{item.strip()}[/]")
            elif k in ("subdomains", "technologies"):
                for item in v_str.split(", "):
                    if item and item.strip():
                        console.print(f"    [{C.C_NEON}]→[/] [{C.C_SILVER}]{item.strip()}[/]")
            elif r.url and k in ("reputation", "status", "valid", "deliverable"):
                console.print(f"    [{C.C_NEON}]→[/] [{C.C_SILVER}]{k}:[/] [{C.C_WHITE}]{v_str}[/]  [{C.C_DIM}]{r.url}[/]")
            else:
                console.print(f"    [{C.C_NEON}]→[/] [{C.C_SILVER}]{k}:[/] [{C.C_WHITE}]{v_str}[/]")

    errors = [r for r in engine.results if r.error]
    if errors:
        console.print()
        for r in errors:
            console.print(Text.from_markup(f"  [{C.C_DIM}]✗[/] [{C.C_DIM}]{r.source}[/] — [{C.C_BLOOD}]{r.error}[/]"))

    console.print()
    duration = ""
    if engine.end_time and engine.start_time:
        d = engine.end_time - engine.start_time
        duration = f" in {d:.1f}s"
    console.print(Text.from_markup(
        f"  [{C.C_DIM}]Scan completed: {len(engine.results)} checks{duration}[/]"
    ))
    console.print()


def save_all_reports(engine):
    report_dir = os.path.join(C.DATA_DIR, "reports")
    os.makedirs(report_dir, exist_ok=True)
    now = datetime.now()
    safe_name = engine.target.replace("@", "_at_").replace(".", "_").replace("+", "")

    txt_path = os.path.join(report_dir, f"{engine.scan_type}_{safe_name}_{now.strftime('%Y%m%d_%H%M%S')}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"VOID OSINT SCAN REPORT\n")
        f.write(f"{'=' * 50}\n")
        f.write(f"Target:  {engine.target}\n")
        f.write(f"Type:    {engine.scan_type.upper()} Intelligence\n")
        f.write(f"Date:    {now.strftime('%d/%m/%Y')}\n")
        f.write(f"Time:    {now.strftime('%H:%M:%S')}\n")
        f.write(f"Found:   {len([r for r in engine.results if r.is_success()])}/{len(engine.results)}\n")
        f.write(f"{'=' * 50}\n\n")
        for r in engine.results:
            status_str = "FOUND" if r.is_success() else ("ERROR" if r.error else "NONE")
            f.write(f"[{status_str:6}] {r.source}\n")
            if r.data:
                for k, v in r.data.items():
                    f.write(f"  {k}: {v}\n")
            if r.error:
                f.write(f"  Error: {r.error}\n")
            f.write("\n")

    console.print(Text.from_markup(
        f"  [{C.C_DIM}]Report saved:[/] [{C.C_MID}]{txt_path}[/]"
    ))

    return [txt_path]
