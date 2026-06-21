"""OSINT Scanner — wraps user-scanner with Void's clean execution UI."""
import asyncio
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed

from rich.table import Table
from rich.text import Text
from rich.padding import Padding
from rich import box

from . import constants as C
from .void_common import ansi_hex as _ansi, console, error_box as _error_box, pause as _pause


def _exec_panel(title, target):
    W = 56
    header = (
        f"[{C.C_BLOOD}]╔{'═' * W}╗[/]\n"
        f"[{C.C_BLOOD}]║[/]  [{C.C_NEON}]VOID SCANNER[/]{' ' * (W - 14)}[{C.C_BLOOD}]║[/]\n"
        f"[{C.C_BLOOD}]║[/]  [{C.C_MID}]{title}[/]{' ' * (W - 2 - len(title))}[{C.C_BLOOD}]║[/]\n"
        f"[{C.C_BLOOD}]╚{'═' * W}╝[/]"
    )
    console.print(Text.from_markup(header))
    console.print(Text.from_markup(f"  [{C.C_SILVER}]Target:[/] [{C.C_WHITE}]{target}[/]"))
    console.print()


def _progress_bar(current, total, width=30):
    pct = current / total if total > 0 else 0
    filled = int(width * pct)
    bar = f"[{C.C_NEON}]{'█' * filled}[/{C.C_DIM}]{'░' * (width - filled)}[/]"
    console.print(f"\r  [{C.C_GOLD}]{current}/{total}[/] {bar} [{C.C_WHITE}]{int(pct*100)}%[/]", end="")


def _print_result(r, is_email, seen_cats):
    cat = getattr(r, "category", "") or ""
    if cat and cat not in seen_cats:
        console.print()
        console.print(Text.from_markup(f"  [{C.C_DIM}]─── {cat.upper()} ───[/]"))
        seen_cats.add(cat)
    if r.is_found():
        txt = r.status.to_label(is_email=r.is_email) if hasattr(r.status, "to_label") else str(r.status.name)
        console.print(
            f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]{r.site_name or '?'}[/]  [{C.C_SILVER}]{txt}[/]"
        )


def _result_table(results, title, target):
    found = [r for r in results if r.is_found()]
    if not found:
        console.print(Text.from_markup(f"\n  [{C.C_NEON}]  ○ No results found for {target}[/]"))
        return

    console.print()
    console.print(Text.from_markup(
        f"[{C.C_BLOOD}]╔{'═' * 56}╗[/]\n"
        f"[{C.C_BLOOD}]║[/]  [{C.C_NEON}]INVESTIGATION RESULT[/]{' ' * 34}[{C.C_BLOOD}]║[/]\n"
        f"[{C.C_BLOOD}]╚{'═' * 56}╝[/]"
    ))
    console.print(Text.from_markup(f"  [{C.C_GOLD}]TARGET:[/]  [{C.C_WHITE}]{target}[/]"))
    console.print(Text.from_markup(f"  [{C.C_GOLD}]STATUS:[/]  [#88FFAA bold]COMPLETED[/]"))
    console.print(Text.from_markup(f"  [{C.C_GOLD}]FOUND:[/]   [{C.C_GOLD}]{len(found)}[/] results"))
    console.print()

    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C.C_BLOOD, show_header=True)
    table.add_column("Site", style=C.C_GOLD, width=22)
    table.add_column("Category", style=C.C_DIM, width=14)
    table.add_column("Status", style=C.C_WHITE, width=16)
    table.add_column("URL", style=C.C_SILVER)
    for r in found:
        status_txt = r.status.to_label(is_email=r.is_email)
        url = getattr(r, "url", "") or ""
        table.add_row(
            r.site_name or "?",
            r.category or "?",
            f"[{C.C_NEON}]{status_txt}[/]",
            f"[link={url}]{url[:50]}[/]" if url else "",
        )
    console.print(Padding(table, (1, 2)))


def _run_email_scan(email, config, seen_cats):
    from user_scanner.core.helpers import (
        load_categories, load_modules, get_scan_func, get_site_name,
    )
    from user_scanner.core.result import Result

    cats = load_categories(is_email=True, no_nsfw=True)
    all_modules = []
    module_cats = {}
    for cat_name, cat_path in cats.items():
        for m in load_modules(cat_path):
            all_modules.append(m)
            module_cats[m.__name__] = cat_name

    total = len(all_modules)

    async def _check_one(module):
        func = get_scan_func(module)
        if not func:
            return Result.error(f"{get_site_name(module)} has no validate_ function")
        site_name = get_site_name(module)
        params = {
            "site_name": site_name.capitalize(),
            "username": email,
            "category": module_cats.get(module.__name__, "Email"),
            "is_email": True,
        }
        try:
            coro = func(email)
            if asyncio.iscoroutine(coro):
                res = await asyncio.wait_for(coro, timeout=15)
            else:
                res = coro
            res.update(**params)
            return res
        except asyncio.TimeoutError:
            return Result.error("Timeout", **params)
        except Exception as e:
            return Result.error(e, **params)

    results = []
    scanned = [0]

    def _on_result(r):
        scanned[0] += 1
        _print_result(r, True, seen_cats)

    async def _runner():
        sem = asyncio.Semaphore(15)
        async def _worker(module):
            async with sem:
                r = await _check_one(module)
                results.append(r)
                _on_result(r)
        await asyncio.gather(*[_worker(m) for m in all_modules])

    asyncio.run(_runner())
    console.print()
    console.print(Text.from_markup(
        f"\n  [{C.C_DIM}]─── SCAN COMPLETE: [{C.C_GOLD}]{len(results)}[/] sites checked ───[/]"
    ))
    return results


def _run_username_scan(username, config, seen_cats):
    from user_scanner.core.helpers import load_categories, load_modules, get_site_name
    from user_scanner.core.orchestrator import _worker_single
    from user_scanner.core.result import Result

    cats = load_categories(is_email=False, no_nsfw=True)
    all_modules = []
    module_cats = {}
    for cat_name, cat_path in cats.items():
        for m in load_modules(cat_path):
            all_modules.append(m)
            module_cats[m.__name__] = cat_name

    total = len(all_modules)
    results = []

    with ThreadPoolExecutor(max_workers=40) as pool:
        fut_to_mod = {pool.submit(_worker_single, m, username, config): m for m in all_modules}
        for fut in as_completed(fut_to_mod, timeout=120):
            m = fut_to_mod[fut]
            try:
                r = fut.result(timeout=5)
                r.update(category=module_cats.get(m.__name__, "Unknown"))
            except Exception:
                r = Result.error("Scan failed", site_name=get_site_name(m).capitalize(), username=username)
            results.append(r)
            _print_result(r, False, seen_cats)

    console.print()
    console.print(Text.from_markup(
        f"\n  [{C.C_DIM}]─── SCAN COMPLETE: [{C.C_GOLD}]{len(results)}[/] sites checked ───[/]"
    ))
    return results


def _run_scan(target, is_email):
    from user_scanner.core.helpers import ScanConfig

    console.print()
    seen_cats = set()

    config = ScanConfig(
        allow_loud=False,
        only_found=True,
        no_nsfw=True,
        verbose=False,
    )

    if is_email:
        results = _run_email_scan(target, config, seen_cats)
    else:
        results = _run_username_scan(target, config, seen_cats)

    return results


def email_intel(email):
    _exec_panel("EMAIL INTELLIGENCE", email)
    results = _run_scan(email, is_email=True)
    _result_table(results, "Email Scan Results", email)
    _save_report(results, email, "email")
    _pause()


def username_intel(username):
    _exec_panel("USERNAME INTELLIGENCE", username)
    results = _run_scan(username, is_email=False)
    _result_table(results, "Username Scan Results", username)
    _save_report(results, username, "username")
    _pause()


def _save_report(results, target, scan_type):
    import json
    from datetime import datetime
    import os

    found = [r for r in results if r.is_found()]
    report_dir = os.path.join(C.DATA_DIR, "reports")
    os.makedirs(report_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = target.replace("@", "_at_").replace(".", "_")

    data = {
        "target": target,
        "type": scan_type,
        "timestamp": datetime.now().isoformat(),
        "total_scanned": len(results),
        "total_found": len(found),
        "results": [
            {
                "site": r.site_name,
                "category": r.category,
                "status": r.status.to_label(is_email=r.is_email),
                "url": getattr(r, "url", ""),
            }
            for r in results
        ],
    }

    json_path = os.path.join(report_dir, f"{scan_type}_{safe_name}_{ts}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    txt_path = os.path.join(report_dir, f"{scan_type}_{safe_name}_{ts}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("VOID OSINT SCAN REPORT\n")
        f.write(f"{'='*50}\n")
        f.write(f"Target: {target}\n")
        f.write(f"Type: {scan_type}\n")
        f.write(f"Timestamp: {data['timestamp']}\n")
        f.write(f"Total Scanned: {data['total_scanned']}\n")
        f.write(f"Total Found: {data['total_found']}\n")
        f.write(f"{'='*50}\n\n")
        for r in found:
            f.write(f"[{r.status.to_label(r.is_email):15}] {r.site_name or '?'}\n")
            if getattr(r, "url", ""):
                f.write(f"  URL: {r.url}\n")
            f.write("\n")

    console.print(Text.from_markup(
        f"\n[{C.C_DIM}]  Reports saved to:[/] [{C.C_MID}]{report_dir}[/]"
    ))
