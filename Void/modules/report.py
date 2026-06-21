"""Report generation — single TXT file + terminal display."""
import os
from datetime import datetime

from rich.text import Text

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
        _print_data(r.data, r.url)

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


def _print_data(data, url=None):
    for k, v in data.items():
        if isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    service = item.get("service", item.get("name", "?"))
                    item_url = item.get("url", item.get("url_user", ""))
                    if item_url:
                        console.print(f"    [{C.C_NEON}]→[/] [{C.C_GOLD}]{service}:[/] [{C.C_WHITE}]{item_url}[/]")
                    else:
                        console.print(f"    [{C.C_NEON}]→[/] [{C.C_SILVER}]{item}[/]")
                else:
                    console.print(f"    [{C.C_NEON}]→[/] [{C.C_SILVER}]{item}[/]")
        elif isinstance(v, dict):
            for dk, dv in v.items():
                if dv:
                    console.print(f"    [{C.C_NEON}]→[/] [{C.C_SILVER}]{dk}:[/] [{C.C_WHITE}]{dv}[/]")
        elif v and str(v) not in ("none", "none found", "N/A", "Unknown", "", "0", "False", "0", "[]", "{}"):
            console.print(f"    [{C.C_NEON}]→[/] [{C.C_SILVER}]{k}:[/] [{C.C_WHITE}]{v}[/]")
    if url:
        console.print(f"    [{C.C_DIM}]→ Link:[/] [{C.C_WHITE}]{url}[/]")


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
                _write_data(f, r.data)
            if r.error:
                f.write(f"  Error: {r.error}\n")
            f.write("\n")

    console.print(Text.from_markup(
        f"  [{C.C_DIM}]Report saved:[/] [{C.C_MID}]{txt_path}[/]"
    ))
    return [txt_path]


def _write_data(f, data, indent=2):
    prefix = " " * indent
    for k, v in data.items():
        if isinstance(v, list):
            for item in v:
                if isinstance(item, dict):
                    service = item.get("service", item.get("name", "?"))
                    item_url = item.get("url", item.get("url_user", ""))
                    if item_url:
                        f.write(f"{prefix}{service}: {item_url}\n")
                    else:
                        f.write(f"{prefix}{item}\n")
                else:
                    f.write(f"{prefix}{item}\n")
        elif isinstance(v, dict):
            for dk, dv in v.items():
                if dv:
                    f.write(f"{prefix}{dk}: {dv}\n")
        elif v and str(v) not in ("none", "none found", "N/A", "Unknown", "", "0", "False"):
            f.write(f"{prefix}{k}: {v}\n")
