"""Dashboard page definitions."""
import os
import sys
import webbrowser

from . import constants as C
from .void_common import panel, console
from rich.panel import Panel as RichPanel
from rich.padding import Padding
from rich.table import Table
from rich.text import Text
from rich import box


_ABOUT_GITHUB = """\
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                     .,,.   ...    :::::::::::: .::.                          ║
║                    ,;;'`';, ;;     ;;;'`````;;;;'`';;,                       ║
║                    [[, _,[[[['     [[[    .n[['   .n[[                       ║
║                     Y$$P"$$$$      $$$  ,$$P"    ``"$$$.                     ║
║                     ,,_,d8"88    .d888,888bo,_   ,,o888"                     ║
║                     "MP"   "YmmMMMM"" `""*UMM   YMMP"                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

Hello, I am 9UZ3.

I'm passionate about cybersecurity, OSINT, and technology as a whole. I enjoy
researching systems, exploring how things work behind the scenes, and expanding
my understanding through experimentation, analysis, and continuous learning.

As a member of Void, a community focused on technology, security, and knowledge
sharing, I spend much of my time studying new concepts, refining technical
skills, and collaborating with people who share the same interest in the
digital world.

For me, technology is not just a field of study but an endless pursuit of
understanding. Every project offers something to learn, every challenge reveals
a new perspective, and every system has details waiting to be discovered.


    ╔
      "You must have chaos within you
      to give birth to a dancing star."

                 — Friedrich Nietzsche
                                        ╝"""


_ABOUT_DISCORD = """\
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║                  _                        .       ..                         ║
║                 u                        @88>   dF                           ║
║                88Nu.   u.         u.     %8P   '88bu.                        ║
║               '88888.o888c  ...ue888b     .    '*88888bu                     ║
║                ^8888  8888  888R Y888r  .@88u    ^"*8888N                    ║
║                 8888  8888  888R I888> ''888E`  beWE "888L                   ║
║                 8888  8888  888R I888>   888E   888E  888E                   ║
║                 8888  8888  888R I888>   888E   888E  888E                   ║
║                .8888b.888P u8888cJ888    888E   888E  888F                   ║
║                 ^Y8888*""   "*888*P"     888&  .888N..888                    ║
║                   `Y"         'Y"        R888"  `"888*""                     ║
║                                           ""       ""                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝

 Void is a community focused on OSINT, cybersecurity, digital research, and
technology. A place created for people who are curious about the digital world
and want to expand their knowledge through collaboration and exploration.

The community brings together researchers, developers, security enthusiasts,
and anyone interested in understanding how information, systems, and technology
work beneath the surface.

Our goal is simple: create a space where curiosity becomes knowledge, and
knowledge becomes capability.


  ╔

        学び続ける者は、成長し続ける。

      "Only the educated are free."

                 — Epictetus
                                   ╝"""


def _show_about(content, url):
    def fn():
        try:
            webbrowser.open(url)
        except Exception:
            pass
        console.print(content)
        console.print(Text.from_markup(f"[{C.C_DIM}]  Enter to return...[/]"))
        input()
    return fn


def _count_reports():
    report_dir = os.path.join(C.DATA_DIR, "reports")
    if not os.path.isdir(report_dir):
        return 0
    return len([f for f in os.listdir(report_dir) if f.endswith((".json", ".txt"))])


def _system_info():
    import shutil
    info = [
        ("Version", f"Void OSINT Toolkit v{C.VERSION}"),
        ("Author", "9uz3"),
        ("Python", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"),
        ("Theme", C.active_theme()),
        ("Terminal", f"{shutil.get_terminal_size((100, 30)).columns}x{shutil.get_terminal_size((100, 30)).lines}"),
        ("Categories", "12"),
        ("Total Tools", "32"),
        ("Config Dir", C.CONFIG_DIR),
        ("Data Dir", C.DATA_DIR),
    ]
    deps = []
    for name, imp in [("dnspython", "dns"), ("phonenumbers", "phonenumbers"),
                        ("Pillow", "PIL"), ("whois", "whois"), ("ipwhois", "ipwhois")]:
        try:
            __import__(imp)
            deps.append(f"✓ {name}")
        except ImportError:
            deps.append(f"✗ {name}")
    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C.C_BLOOD, show_header=False)
    table.add_column("Field", style=C.C_SILVER, width=16)
    table.add_column("Value", style=C.C_WHITE)
    for field, value in info:
        table.add_row(field, value)
    table2 = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C.C_BLOOD, show_header=False)
    table2.add_column("Dependency", style=C.C_SILVER, width=16)
    table2.add_column("Status", style=C.C_WHITE)
    for d in deps:
        status, name = d.split(" ", 1)
        style = C.C_NEON if status == "✓" else C.C_DIM
        table2.add_row(name, f"[{style}]{status}[/]")
    console.print(Padding(RichPanel(table, title=f"[bold {C.C_GOLD}]System Info[/]",
                                  border_style=C.C_BLOOD, padding=(1, 2)), (1, 0)))
    console.print(Padding(RichPanel(table2, title=f"[bold {C.C_GOLD}]Dependencies[/]",
                                  border_style=C.C_BLOOD, padding=(1, 2)), (0, 0)))
    input(f"\033[38;2;120;0;0m  ► Enter to return...\033[0m")


def _home_dashboard():
    from datetime import datetime
    import shutil
    s = C.active_theme()
    n_reports = _count_reports()
    deps_ok = 0
    deps_total = 5
    for imp in ["dns", "phonenumbers", "PIL", "whois", "ipwhois"]:
        try:
            __import__(imp)
            deps_ok += 1
        except ImportError:
            pass

    col, rows = shutil.get_terminal_size((100, 30))
    lines = []
    lines.append(Text.from_markup(
        f"[{C.C_NEON}]  STATUS:[/]        [#88FFAA bold]ONLINE[/]"
    ))
    lines.append(Text.from_markup(
        f"[{C.C_NEON}]  SYSTEM:[/]        [{C.C_WHITE}]VOID OSINT TOOLKIT[/]"
    ))
    lines.append(Text.from_markup(
        f"[{C.C_NEON}]  VERSION:[/]       [{C.C_WHITE}]{C.VERSION}[/]"
    ))
    lines.append(Text.from_markup(
        f"[{C.C_NEON}]  MODULES:[/]       [{C.C_GOLD}]32[/] AVAILABLE"
    ))
    lines.append(Text.from_markup(
        f"[{C.C_NEON}]  TOOLS:[/]         [{C.C_GOLD}]{deps_ok}/{deps_total}[/] LOADED"
    ))
    lines.append(Text.from_markup(
        f"[{C.C_NEON}]  THEME:[/]         [{C.C_WHITE}]{s.upper()}[/]"
    ))
    lines.append(Text.from_markup(
        f"[{C.C_NEON}]  REPORTS:[/]       [{C.C_GOLD}]{n_reports}[/] SAVED"
    ))
    lines.append(Text.from_markup(
        f"[{C.C_NEON}]  LAST UPDATE:[/]   [{C.C_WHITE}]{datetime.now().strftime('%Y-%m-%d %H:%M')}[/]"
    ))

    console.print(Padding(RichPanel(
        lines,
        title=f"[bold {C.C_GOLD}]SYSTEM STATUS[/]",
        border_style=C.C_BLOOD,
        box=box.DOUBLE_EDGE,
        padding=(1, 2),
    ), (1, 2)))

    shortcuts = Table(box=box.MINIMAL, border_style=C.C_BLOOD, show_header=False, padding=(0, 2))
    shortcuts.add_column("Action", style=C.C_GOLD, width=16)
    shortcuts.add_column("Key", style=C.C_WHITE)
    shortcuts.add_row("Navigate", "↑ ↓ ← →")
    shortcuts.add_row("Select", "ENTER")
    shortcuts.add_row("Search", "F")
    shortcuts.add_row("Quit", "Q / Ctrl+C")
    console.print(Padding(RichPanel(
        shortcuts,
        title=f"[bold {C.C_GOLD}]QUICK CONTROLS[/]",
        border_style=C.C_BLOOD,
        padding=(1, 1),
    ), (0, 2)))

    console.print()
    console.print(Text.from_markup(f"[{C.C_DIM}]  Select a category from the sidebar to begin.[/]"))
    console.print(Text.from_markup(f"[{C.C_DIM}]  Press F to search across all tools.[/]"))
    input(f"\033[38;2;120;0;0m  ► Enter to return...\033[0m")


def _panel_tool(title, desc):
    def fn():
        panel(title, desc)
        console.print(RichPanel(
            Text.from_markup(f"[{C.C_SILVER}]This tool opens resources in your browser.[/]"),
            border_style=C.C_BLOOD, padding=(1, 2),
        ))
        input(f"\033[38;2;120;0;0m  ► Enter to return...\033[0m")
    return fn


def build_pages_data():
    from .tools_osint import (
        tool_email_lookup, tool_email_validate, tool_email_breach,
        tool_phone_lookup, tool_phone_carrier,
        tool_ip_geo, tool_ip_vpn, tool_ip_whois,
        tool_username_search, tool_username_analyze,
        tool_domain_whois, tool_dns_lookup, tool_ssl_cert,
        tool_social_search, tool_social_scan,
        tool_breach_check, tool_breach_search,
        tool_web_tech, tool_web_headers, tool_web_robots,
        tool_dork_gen, tool_dork_search,
        tool_exif_viewer, tool_image_meta,
    )

    pages = {
        "home": [
            ("00", "Dashboard", _home_dashboard),
            ("01", "GitHub", _show_about(_ABOUT_GITHUB, C.GITHUB)),
            ("02", "Discord", _show_about(_ABOUT_DISCORD, C.DISCORD)),
            ("03", "Changelog", _panel_tool("Changelog", "Version history")),
            ("04", "System Info", _system_info),
            ("05", "Setup Config", lambda: __import__("lib.setup", fromlist=["x"]).run_setup_wizard(force=True)),
            ("Q", "Quit System", lambda: sys.exit(0)),
        ],
        "email-osint": [
            ("01", "Email Lookup", tool_email_lookup),
            ("02", "Email Validate", tool_email_validate),
            ("03", "Email Breach Check", tool_email_breach),
        ],
        "phone-osint": [
            ("01", "Phone Lookup", tool_phone_lookup),
            ("02", "Phone Carrier", tool_phone_carrier),
        ],
        "ip-osint": [
            ("01", "IP Geolocation", tool_ip_geo),
            ("02", "IP VPN Detection", tool_ip_vpn),
            ("03", "IP WHOIS", tool_ip_whois),
        ],
        "username-osint": [
            ("01", "Username Search", tool_username_search),
            ("02", "Username Analyze", tool_username_analyze),
        ],
        "domain-osint": [
            ("01", "Domain WHOIS", tool_domain_whois),
            ("02", "DNS Lookup", tool_dns_lookup),
            ("03", "SSL Certificate", tool_ssl_cert),
        ],
        "social-osint": [
            ("01", "Social Search", tool_social_search),
            ("02", "Social Scan", tool_social_scan),
        ],
        "breach-osint": [
            ("01", "Breach Check", tool_breach_check),
            ("02", "Breach Search", tool_breach_search),
        ],
        "web-osint": [
            ("01", "Web Tech Detect", tool_web_tech),
            ("02", "Web Headers", tool_web_headers),
            ("03", "Web Robots", tool_web_robots),
        ],
        "dork-osint": [
            ("01", "Dork Generator", tool_dork_gen),
            ("02", "Dork Search", tool_dork_search),
        ],
        "image-osint": [
            ("01", "EXIF Viewer", tool_exif_viewer),
            ("02", "Image Metadata", tool_image_meta),
        ],
        "about": [
            ("01", "Version Info", _panel_tool("Version", f"Void OSINT Toolkit v{C.VERSION}")),
            ("02", "Author", _show_about(_ABOUT_GITHUB, C.GITHUB)),
        ],
    }
    return pages
