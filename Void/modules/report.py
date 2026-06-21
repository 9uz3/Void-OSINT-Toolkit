"""Report generation — JSON, TXT, and HTML formats."""
import json
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

    console.print()
    console.print(Text.from_markup(
        f"[{C.C_BLOOD}]╔{'═' * 56}╗[/]\n"
        f"[{C.C_BLOOD}]║[/]  [{C.C_NEON}]INVESTIGATION RESULT[/]{' ' * 34}[{C.C_BLOOD}]║[/]\n"
        f"[{C.C_BLOOD}]╚{'═' * 56}╝[/]"
    ))
    console.print()
    console.print(Text.from_markup(f"  [{C.C_GOLD}]TARGET:[/]   [{C.C_WHITE}]{engine.target}[/]"))
    console.print(Text.from_markup(f"  [{C.C_GOLD}]TYPE:[/]     [{C.C_WHITE}]{engine.scan_type.upper()} INTELLIGENCE[/]"))
    console.print(Text.from_markup(f"  [{C.C_GOLD}]STATUS:[/]   [#88FFAA bold]COMPLETED[/]"))
    console.print()

    console.print(Text.from_markup(f"  [{C.C_GOLD}]FINDINGS:[/]"))
    if found:
        for r in found:
            console.print(f"    [{C.C_NEON}]✓[/] [{C.C_GOLD}]{r.source}[/] — {r.status}")
    else:
        console.print(f"    [{C.C_DIM}]No positive results found[/]")

    if errors:
        console.print()
        console.print(Text.from_markup(f"  [{C.C_DIM}]ERRORS:[/]"))
        for r in errors:
            console.print(f"    [{C.C_BLOOD}]✗[/] [{C.C_DIM}]{r.source}[/] — {r.error}")

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
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = engine.target.replace("@", "_at_").replace(".", "_").replace("+", "")

    paths = []

    json_path = os.path.join(report_dir, f"{engine.scan_type}_{safe_name}_{ts}.json")
    data = {
        "target": engine.target,
        "type": engine.scan_type,
        "timestamp": datetime.now().isoformat(),
        "duration": (engine.end_time - engine.start_time) if engine.end_time and engine.start_time else 0,
        "total_checks": len(engine.results),
        "total_found": len([r for r in engine.results if r.is_success()]),
        "results": [r.to_dict() for r in engine.results],
    }
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    paths.append(json_path)

    txt_path = os.path.join(report_dir, f"{engine.scan_type}_{safe_name}_{ts}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(f"VOID OSINT SCAN REPORT\n")
        f.write(f"{'=' * 50}\n")
        f.write(f"Target:  {engine.target}\n")
        f.write(f"Type:    {engine.scan_type}\n")
        f.write(f"Time:    {data['timestamp']}\n")
        f.write(f"Found:   {data['total_found']}/{data['total_checks']}\n")
        f.write(f"{'=' * 50}\n\n")
        for r in engine.results:
            status_str = "FOUND" if r.is_success() else ("ERROR" if r.error else "NONE")
            f.write(f"[{status_str:6}] {r.source}: {r.status}\n")
            if r.url:
                f.write(f"  URL: {r.url}\n")
            if r.data:
                for k, v in r.data.items():
                    f.write(f"  {k}: {v}\n")
            f.write("\n")
    paths.append(txt_path)

    html_path = os.path.join(report_dir, f"{engine.scan_type}_{safe_name}_{ts}.html")
    _generate_html(engine, html_path, data)
    paths.append(html_path)

    console.print(Text.from_markup(
        f"\n  [{C.C_DIM}]Reports saved to:[/] [{C.C_MID}]{report_dir}[/]"
    ))
    console.print(Text.from_markup(
        f"  [{C.C_DIM}]  ├─ JSON:[/] [{C.C_WHITE}]{os.path.basename(json_path)}[/]"
    ))
    console.print(Text.from_markup(
        f"  [{C.C_DIM}]  ├─ TXT:[/]  [{C.C_WHITE}]{os.path.basename(txt_path)}[/]"
    ))
    console.print(Text.from_markup(
        f"  [{C.C_DIM}]  └─ HTML:[/] [{C.C_WHITE}]{os.path.basename(html_path)}[/]"
    ))

    return paths


def _generate_html(engine, path, data):
    found = [r for r in engine.results if r.is_success()]
    errors = [r for r in engine.results if r.error]

    results_rows = ""
    for r in engine.results:
        status_color = "#00ff88" if r.is_success() else ("#ff4444" if r.error else "#888888")
        status_text = r.status.upper()
        error_text = f'<span style="color:#ff4444">{r.error}</span>' if r.error else ""
        url_cell = f'<a href="{r.url}" style="color:#4488ff">{r.url[:60]}</a>' if r.url else ""
        data_cell = "<br>".join(f"<b>{k}:</b> {v}" for k, v in r.data.items()) if r.data else ""

        results_rows += f"""
        <tr>
            <td style="color:#ffd700">{r.source}</td>
            <td>{r.category}</td>
            <td style="color:{status_color}">{status_text}</td>
            <td>{url_cell}</td>
            <td>{data_cell}{error_text}</td>
        </tr>"""

    duration = f"{engine.end_time - engine.start_time:.1f}s" if engine.end_time and engine.start_time else "N/A"

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>VOID OSINT Report — {engine.target}</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{ background: #0a0a0a; color: #cccccc; font-family: 'Courier New', monospace; padding: 20px; }}
  .header {{ border: 2px solid #ff2020; padding: 20px; margin-bottom: 20px; text-align: center; }}
  .header h1 {{ color: #ff2020; font-size: 24px; letter-spacing: 4px; }}
  .header .subtitle {{ color: #888888; margin-top: 5px; }}
  .info {{ display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 20px; }}
  .info-box {{ border: 1px solid #333; padding: 12px; }}
  .info-box .label {{ color: #ffd700; font-size: 12px; text-transform: uppercase; }}
  .info-box .value {{ color: #ffffff; font-size: 16px; margin-top: 4px; }}
  table {{ width: 100%; border-collapse: collapse; border: 1px solid #333; }}
  th {{ background: #1a1a1a; color: #ffd700; padding: 10px; text-align: left; border-bottom: 2px solid #ff2020; }}
  td {{ padding: 8px 10px; border-bottom: 1px solid #222; }}
  tr:hover {{ background: #111; }}
  .found {{ color: #00ff88; }}
  .error {{ color: #ff4444; }}
  .footer {{ margin-top: 20px; text-align: center; color: #444; font-size: 12px; border-top: 1px solid #222; padding-top: 10px; }}
</style>
</head>
<body>
  <div class="header">
    <h1>VOID OSINT — INVESTIGATION REPORT</h1>
    <div class="subtitle">Generated by Void OSINT Toolkit v{C.VERSION}</div>
  </div>
  <div class="info">
    <div class="info-box"><div class="label">Target</div><div class="value">{engine.target}</div></div>
    <div class="info-box"><div class="label">Type</div><div class="value">{engine.scan_type.upper()} Intelligence</div></div>
    <div class="info-box"><div class="label">Status</div><div class="value found">COMPLETED</div></div>
    <div class="info-box"><div class="label">Duration</div><div class="value">{duration}</div></div>
    <div class="info-box"><div class="label">Total Checks</div><div class="value">{len(engine.results)}</div></div>
    <div class="info-box"><div class="label">Results Found</div><div class="value found">{len(found)}</div></div>
  </div>
  <table>
    <thead>
      <tr><th>Source</th><th>Category</th><th>Status</th><th>URL</th><th>Details</th></tr>
    </thead>
    <tbody>
      {results_rows}
    </tbody>
  </table>
  <div class="footer">
    VOID OSINT Toolkit v{C.VERSION} — {data['timestamp']} — For authorized use only
  </div>
</body>
</html>"""

    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
