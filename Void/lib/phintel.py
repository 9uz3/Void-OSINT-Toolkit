"""Phone Intelligence — comprehensive phone number analysis module."""
import json
import os
from datetime import datetime

from rich.table import Table
from rich.text import Text
from rich.padding import Padding
from rich import box

from . import constants as C
from .void_common import ansi_hex as _ansi, console, error_box as _error_box, pause as _pause

# High-risk country codes (Premium/paid services)
_HIGH_RISK_CC = {
    "1": "North America (premium)",
    "44": "UK (premium)",
    "61": "Australia (premium)",
    "33": "France (premium)",
    "49": "Germany (premium)",
}

# Known test/disposable number prefixes
_TEST_PREFIXES = ["555", "000", "123"]


def _exec_panel(title, target):
    header = (
        f"[{C.C_BLOOD}]╔{'═' * 56}╗[/]\n"
        f"[{C.C_BLOOD}]║[/]  [{C.C_NEON}]VOID PHONE INTEL[/]{' ' * (56 - 18)}[{C.C_BLOOD}]║[/]\n"
        f"[{C.C_BLOOD}]║[/]  [{C.C_MID}]{title}[/]{' ' * (56 - 2 - len(title))}[{C.C_BLOOD}]║[/]\n"
        f"[{C.C_BLOOD}]╚{'═' * 56}╝[/]"
    )
    console.print(Text.from_markup(header))
    console.print(Text.from_markup(f"  [{C.C_SILVER}]Target:[/] [{C.C_WHITE}]{target}[/]"))


def _risk_label(score):
    if score >= 70:
        return f"[{C.C_BLOOD}]HIGH[/]"
    if score >= 40:
        return f"[{C.C_GOLD}]MEDIUM[/]"
    return f"[{C.C_NEON}]LOW[/]"


def _analyze_phone(number):
    import phonenumbers
    from phonenumbers import carrier, geocoder, timezone, PhoneNumberType

    pn = phonenumbers.parse(number, None)
    is_valid = phonenumbers.is_valid_number(pn)
    is_possible = phonenumbers.is_possible_number(pn)
    cc = pn.country_code
    national = str(pn.national_number)
    type_map = {
        PhoneNumberType.MOBILE: "Mobile",
        PhoneNumberType.FIXED_LINE: "Landline",
        PhoneNumberType.FIXED_LINE_OR_MOBILE: "Mobile/Landline",
        PhoneNumberType.VOIP: "VoIP",
        PhoneNumberType.TOLL_FREE: "Toll-Free",
        PhoneNumberType.PREMIUM_RATE: "Premium Rate",
        PhoneNumberType.SHARED_COST: "Shared Cost",
        PhoneNumberType.PERSONAL_NUMBER: "Personal",
        PhoneNumberType.PAGER: "Pager",
        PhoneNumberType.UAN: "UAN",
        PhoneNumberType.VOICEMAIL: "Voicemail",
        PhoneNumberType.UNKNOWN: "Unknown",
    }
    num_type = type_map.get(phonenumbers.number_type(pn), "Unknown")

    country_name = geocoder.description_for_number(pn, "en") or "Unknown"
    carrier_name = carrier.name_for_number(pn, "en") or "Unknown"
    tz_list = timezone.time_zones_for_number(pn) or []
    tz_str = ", ".join(tz_list) if tz_list else "Unknown"

    fmt_international = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    fmt_national = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.NATIONAL)
    fmt_e164 = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)

    risk = 0
    if not is_valid:
        risk += 50
    if any(national.startswith(p) for p in _TEST_PREFIXES):
        risk += 30
    if str(cc) in _HIGH_RISK_CC:
        risk += 20

    info = {
        "raw": number,
        "e164": fmt_e164,
        "international": fmt_international,
        "national": fmt_national,
        "valid": is_valid,
        "possible": is_possible,
        "country_code": f"+{cc}",
        "country": country_name,
        "carrier": carrier_name,
        "line_type": num_type,
        "timezone": tz_str,
        "national_number": national,
        "risk_score": min(risk, 100),
    }
    return info


def phone_intel(number):
    _exec_panel("PHONE INVESTIGATION", number)

    try:
        info = _analyze_phone(number)
    except ImportError:
        _error_box("Missing dep", "Install phonenumbers: pip install phonenumbers")
        _pause()
        return
    except Exception as e:
        _error_box("Phone Analysis", str(e))
        _pause()
        return

    console.print()
    console.print(Text.from_markup(f"  [{C.C_DIM}]─── BASIC INFO ───[/]"))
    console.print(f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]Valid:[/]         [{C.C_WHITE}]{'✓ YES' if info['valid'] else '✗ NO'}[/]")
    console.print(f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]Possible:[/]      [{C.C_WHITE}]{'✓ YES' if info['possible'] else '✗ NO'}[/]")
    console.print(f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]International:[/] [{C.C_SILVER}]{info['international']}[/]")
    console.print(f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]National:[/]      [{C.C_SILVER}]{info['national']}[/]")
    console.print(f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]E.164:[/]         [{C.C_WHITE}]{info['e164']}[/]")

    console.print()
    console.print(Text.from_markup(f"  [{C.C_DIM}]─── LOCATION & CARRIER ───[/]"))
    console.print(f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]Country:[/]       [{C.C_WHITE}]{info['country']}[/] [{C.C_SILVER}]({info['country_code']})[/]")
    console.print(f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]Carrier:[/]       [{C.C_WHITE}]{info['carrier']}[/]")
    console.print(f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]Line Type:[/]     [{C.C_WHITE}]{info['line_type']}[/]")
    console.print(f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]Timezone:[/]      [{C.C_WHITE}]{info['timezone']}[/]")

    console.print()
    console.print(Text.from_markup(f"  [{C.C_DIM}]─── RISK ASSESSMENT ───[/]"))
    risk_str = _risk_label(info['risk_score'])
    console.print(f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]Risk Score:[/]    {risk_str}  [{C.C_SILVER}]({info['risk_score']}/100)[/]")

    console.print()
    _result_table(info)
    _save_report(info)
    _pause()


def _result_table(info):
    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C.C_BLOOD, show_header=True)
    table.add_column("Field", style=C.C_GOLD, width=18)
    table.add_column("Value", style=C.C_WHITE, width=40)
    for key, label in [
        ("international", "International"),
        ("national", "National"),
        ("e164", "E.164"),
        ("country", "Country"),
        ("country_code", "Country Code"),
        ("carrier", "Carrier"),
        ("line_type", "Line Type"),
        ("timezone", "Timezone"),
    ]:
        table.add_row(label, info.get(key, "?"))
    table.add_row("Valid", "✓ YES" if info.get("valid") else "✗ NO")
    table.add_row("Risk Score", f"{info.get('risk_score', '?')}/100")
    console.print()
    console.print(Padding(table, (1, 2)))


def _save_report(info):
    report_dir = os.path.join(C.DATA_DIR, "reports")
    os.makedirs(report_dir, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_name = info["raw"].replace("+", "").replace(" ", "_")

    data = {
        "target": info["raw"],
        "type": "phone",
        "timestamp": datetime.now().isoformat(),
        "results": info,
    }

    json_path = os.path.join(report_dir, f"phone_{safe_name}_{ts}.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    txt_path = os.path.join(report_dir, f"phone_{safe_name}_{ts}.txt")
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write("VOID OSINT REPORT — PHONE INTELLIGENCE\n")
        f.write(f"{'='*50}\n")
        f.write(f"Target: {info['raw']}\n")
        f.write(f"Timestamp: {data['timestamp']}\n")
        f.write(f"{'='*50}\n\n")
        for k, v in info.items():
            if isinstance(v, bool):
                v = "YES" if v else "NO"
            f.write(f"{k.replace('_', ' ').title():20} {v}\n")

    console.print(Text.from_markup(
        f"\n[{C.C_DIM}]  Reports saved to:[/] [{C.C_MID}]{report_dir}[/]"
    ))


def phone_carrier_intel(number):
    import phonenumbers
    from phonenumbers import carrier

    try:
        pn = phonenumbers.parse(number, None)
        c = carrier.name_for_number(pn, "en") or "Unknown"
        cc = pn.country_code
        console.print()
        console.print(f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]Carrier:[/]       [{C.C_WHITE}]{c}[/]")
        console.print(f"  [{C.C_NEON}]✔[/]  [{C.C_GOLD}]Country Code:[/]  [{C.C_WHITE}]+{cc}[/]")
    except Exception as e:
        _error_box("Carrier Analysis", str(e))
