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
    found = [r for r in engine.results if r.is_success()]
    errors = [r for r in engine.results if r.error]
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

    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C.C_BLOOD, show_header=True)
    table.add_column("Source", style=C.C_GOLD, width=22)
    table.add_column("Status", style=C.C_WHITE, width=14)
    table.add_column("Details", style=C.C_SILVER)

    for r in engine.results:
        if r.is_success():
            detail = ", ".join(f"{k}: {v}" for k, v in list(r.data.items())[:3])
            table.add_row(r.source, f"[#88FFAA]FOUND[/]", detail)
        elif r.error:
            table.add_row(r.source, f"[#FF4444]ERROR[/]", r.error[:50])
        else:
            table.add_row(r.source, f"[{C.C_DIM}]NONE[/]", "-")

    console.print(Padding(table, (1, 2)))

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
