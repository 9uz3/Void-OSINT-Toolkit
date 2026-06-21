"""OSINT tool implementations — all built-in, no external scripts needed."""
import json
import os
import re
import ssl
import socket
import sys
import urllib.parse
import urllib.request
import urllib.error
from datetime import datetime

from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.padding import Padding
from rich import box

from . import constants as C
from .void_common import (
    ansi_hex as _ansi, console, error_box as _error_box,
    panel as _panel, pause as _pause, success_box as _success_box,
)

C_BLOOD = C.C_BLOOD
C_MID = C.C_MID
C_NEON = C.C_NEON
C_WHITE = C.C_WHITE
C_SILVER = C.C_SILVER
C_DIM = C.C_DIM
C_GOLD = C.C_GOLD
C_GOLD2 = C.C_GOLD2


def _fetch_json(url, timeout=10):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "application/json",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def _fetch_text(url, timeout=10):
    req = urllib.request.Request(url, headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    })
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", errors="ignore")


def _show_table(title, rows, border_style=None):
    if border_style is None:
        border_style = C_BLOOD
    console.print()
    console.print(Text.from_markup(
        f"[{C_BLOOD}]╔{'═' * 56}╗[/]\n"
        f"[{C_BLOOD}]║[/]  [{C_NEON}]{title}[/]{' ' * (56 - 2 - len(title))}[{C_BLOOD}]║[/]\n"
        f"[{C_BLOOD}]╚{'═' * 56}╝[/]"
    ))
    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=border_style, show_header=False)
    table.add_column("Field", style=C_SILVER, width=22)
    table.add_column("Value", style=C_WHITE)
    for field, value in rows:
        table.add_row(field, str(value))
    console.print(Padding(table, (1, 2)))


_USERNAME_SITES = [
    ("GitHub",    "https://github.com/{u}"),
    ("Twitter/X", "https://x.com/{u}"),
    ("Instagram", "https://instagram.com/{u}"),
    ("Reddit",    "https://reddit.com/user/{u}"),
    ("Twitch",    "https://twitch.tv/{u}"),
    ("YouTube",   "https://youtube.com/@{u}"),
    ("Telegram",  "https://t.me/{u}"),
    ("Medium",    "https://medium.com/@{u}"),
    ("Pinterest", "https://pinterest.com/{u}"),
    ("Snapchat",  "https://snapchat.com/add/{u}"),
    ("Steam",     "https://steamcommunity.com/id/{u}"),
    ("TikTok",    "https://tiktok.com/@{u}"),
    ("Facebook",  "https://facebook.com/{u}"),
    ("Dev.to",    "https://dev.to/{u}"),
    ("Keybase",   "https://keybase.io/{u}"),
    ("Replit",    "https://replit.com/@{u}"),
    ("Glitch",    "https://glitch.com/@{u}"),
]


def _extract_domain(url):
    from urllib.parse import urlparse
    return urlparse(url).netloc


# ── EMAIL OSINT ──────────────────────────────────────────────

def tool_email_lookup():
    from core.engine import OSINTEngine
    _panel("EMAIL INTELLIGENCE", "Full email investigation (100+ platforms)")
    email = input(f"{_ansi(C_MID)}  Email >> \033[0m").strip()
    if not email: return
    engine = OSINTEngine()
    engine.run_email_scan(email)
    engine.show_results()
    engine.save_reports()
    _pause()


def tool_email_validate():
    from core.engine import OSINTEngine
    _panel("EMAIL VALIDATE", "Check email registration across platforms")
    email = input(f"{_ansi(C_MID)}  Email >> \033[0m").strip()
    if not email: return
    engine = OSINTEngine()
    engine.run_email_scan(email)
    engine.show_results()
    engine.save_reports()
    _pause()


def tool_email_breach():
    from core.engine import OSINTEngine
    _panel("EMAIL BREACH CHECK", "Scan email across services + breach data")
    email = input(f"{_ansi(C_MID)}  Email >> \033[0m").strip()
    if not email: return
    engine = OSINTEngine()
    engine.run_email_scan(email)
    engine.show_results()
    engine.save_reports()
    _pause()


# ── PHONE OSINT ──────────────────────────────────────────────

def tool_phone_lookup():
    from core.engine import OSINTEngine
    _panel("PHONE INTELLIGENCE", "Full phone number analysis")
    phone = input(f"{_ansi(C_MID)}  Phone (+CCXXXXXXXXX) >> \033[0m").strip()
    if not phone: return
    engine = OSINTEngine()
    engine.run_phone_scan(phone)
    engine.show_results()
    engine.save_reports()
    _pause()


def tool_phone_carrier():
    from core.engine import OSINTEngine
    _panel("PHONE CARRIER", "Carrier identification")
    phone = input(f"{_ansi(C_MID)}  Phone (+CCXXXXXXXXX) >> \033[0m").strip()
    if not phone: return
    engine = OSINTEngine()
    engine.run_phone_scan(phone)
    engine.show_results()
    engine.save_reports()
    _pause()


# ── IP OSINT ─────────────────────────────────────────────────

def tool_ip_geo():
    from core.engine import OSINTEngine
    _panel("IP GEOLOCATION", "Get geolocation data for an IP address")
    ip = input(f"{_ansi(C_MID)}  IP Address >> \033[0m").strip()
    if not ip: return
    engine = OSINTEngine()
    engine.run_ip_scan(ip)
    engine.show_results()
    engine.save_reports()
    _pause()


def tool_ip_vpn():
    from core.engine import OSINTEngine
    _panel("IP VPN DETECTION", "Detect VPN/Proxy/Tor on an IP")
    ip = input(f"{_ansi(C_MID)}  IP Address >> \033[0m").strip()
    if not ip: return
    engine = OSINTEngine()
    engine.run_ip_scan(ip)
    engine.show_results()
    engine.save_reports()
    _pause()


def tool_ip_whois():
    from core.engine import OSINTEngine
    _panel("IP WHOIS", "WHOIS lookup for IP address")
    ip = input(f"{_ansi(C_MID)}  IP Address >> \033[0m").strip()
    if not ip: return
    engine = OSINTEngine()
    engine.run_ip_scan(ip)
    engine.show_results()
    engine.save_reports()
    _pause()


# ── USERNAME OSINT ───────────────────────────────────────────

def tool_username_search():
    from core.engine import OSINTEngine
    _panel("USERNAME SEARCH", "Full username investigation (185+ platforms)")
    u = input(f"{_ansi(C_MID)}  Username >> \033[0m").strip()
    if not u: return
    engine = OSINTEngine()
    engine.run_username_scan(u)
    engine.show_results()
    engine.save_reports()
    _pause()


def tool_username_analyze():
    _panel("USERNAME ANALYZE", "Analyze username pattern & entropy")
    u = input(f"{_ansi(C_MID)}  Username >> \033[0m").strip()
    if not u: return
    patterns = []
    if re.search(r'\d', u):
        patterns.append("Contains numbers")
    if re.search(r'[A-Z]', u):
        patterns.append("Contains uppercase")
    if re.search(r'[a-z]', u):
        patterns.append("Contains lowercase")
    if re.search(r'[^a-zA-Z0-9_]', u):
        patterns.append("Contains special chars")
    if '_' in u:
        patterns.append("Uses underscores")
    if '.' in u:
        patterns.append("Uses dots")
    if len(u) < 5:
        patterns.append("Short (<5 chars)")

    entropy = 0
    chars = set(u)
    if re.search(r'[a-z]', u): entropy += 26
    if re.search(r'[A-Z]', u): entropy += 26
    if re.search(r'\d', u):   entropy += 10
    if re.search(r'[^a-zA-Z0-9]', u): entropy += 32
    bits = len(u) * (entropy.bit_length() - 1) if entropy else 0

    rows = [
        ("Username", u),
        ("Length", str(len(u))),
        ("Entropy", f"{bits} bits"),
    ]
    if patterns:
        rows.append(("Patterns", ", ".join(patterns)))
    _show_table("Username Analysis", rows)
    _pause()


# ── DOMAIN OSINT ─────────────────────────────────────────────

def tool_domain_whois():
    from core.engine import OSINTEngine
    _panel("DOMAIN WHOIS", "WHOIS lookup for domain")
    d = input(f"{_ansi(C_MID)}  Domain (ex: example.com) >> \033[0m").strip()
    if not d: return
    engine = OSINTEngine()
    engine.run_domain_scan(d)
    engine.show_results()
    engine.save_reports()
    _pause()


def tool_dns_lookup():
    from core.engine import OSINTEngine
    _panel("DNS LOOKUP", "DNS record lookup for domain")
    d = input(f"{_ansi(C_MID)}  Domain >> \033[0m").strip()
    if not d: return
    engine = OSINTEngine()
    engine.run_domain_scan(d)
    engine.show_results()
    engine.save_reports()
    _pause()


def tool_ssl_cert():
    from core.engine import OSINTEngine
    _panel("SSL CERTIFICATE", "Fetch SSL certificate info for domain")
    d = input(f"{_ansi(C_MID)}  Domain >> \033[0m").strip()
    if not d: return
    engine = OSINTEngine()
    engine.run_domain_scan(d)
    engine.show_results()
    engine.save_reports()
    _pause()


# ── SOCIAL OSINT ─────────────────────────────────────────────

def tool_social_search():
    _panel("SOCIAL SEARCH", "Search social media profiles and content")
    query = input(f"{_ansi(C_MID)}  Search query >> \033[0m").strip()
    if not query: return
    links = [
        ("Google", f"https://google.com/search?q={urllib.parse.quote(query)}"),
        ("Twitter/X", f"https://x.com/search?q={urllib.parse.quote(query)}"),
        ("Reddit", f"https://reddit.com/search?q={urllib.parse.quote(query)}"),
        ("Facebook", f"https://facebook.com/search/top?q={urllib.parse.quote(query)}"),
        ("LinkedIn", f"https://linkedin.com/search/results/all/?keywords={urllib.parse.quote(query)}"),
        ("TikTok", f"https://tiktok.com/search?q={urllib.parse.quote(query)}"),
    ]
    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C_BLOOD, show_header=False)
    table.add_column("Platform", style=C_GOLD, width=14)
    table.add_column("Search URL", style=C_WHITE)
    for name, url in links:
        table.add_row(name, f"[link={url}]{url}[/]")
    console.print(Padding(table, (1, 2)))
    console.print(Text.from_markup(f"[{C_DIM}]  Ctrl+click to open in browser[/]"))
    _pause()


def tool_social_scan():
    _panel("SOCIAL SCAN", "Scan public info across social platforms")
    query = input(f"{_ansi(C_MID)}  Username / query >> \033[0m").strip()
    if not query: return
    console.print(Text.from_markup(f"[{C_NEON} bold] ┌── Checking username across services...\n"))
    import urllib.request
    sites = [
        ("Twitter/X",  f"https://x.com/{query}"),
        ("Instagram",  f"https://instagram.com/{query}"),
        ("Reddit",     f"https://reddit.com/user/{query}"),
        ("TikTok",     f"https://tiktok.com/@{query}"),
        ("GitHub",     f"https://github.com/{query}"),
        ("YouTube",    f"https://youtube.com/@{query}"),
    ]
    for name, url in sites:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            code = urllib.request.urlopen(req, timeout=5).getcode()
            status = f"[{C_NEON}]✗ FOUND[/]" if code == 200 else f"[{C_DIM}]~ {code}[/]"
            console.print(f"  {status} [{C_GOLD}]{name:12}[/] {url}")
        except urllib.error.HTTPError as e:
            s = f"[{C_WHITE}]✓ None[/]" if e.code == 404 else f"[{C_DIM}]~ {e.code}[/]"
            console.print(f"  {s} [{C_DIM}]{name:12}[/] {url}")
        except Exception:
            console.print(f"  [{C_DIM}]~ error[/] [{C_DIM}]{name:12}[/]")
    _pause()


# ── BREACH OSINT ─────────────────────────────────────────────

def tool_breach_check():
    _panel("BREACH CHECK", "Check if email appears in known breaches")
    email = input(f"{_ansi(C_MID)}  Email >> \033[0m").strip()
    if not email: return
    console.print(Text.from_markup(f"[{C_NEON} bold] ┌── Checking EmailRep.io..."))
    try:
        data = _fetch_json(f"https://emailrep.io/{urllib.parse.quote(email)}", timeout=8)
        if "email" in data:
            details = data.get("details", {})
            rows = [
                ("Email", data.get("email", email)),
                ("Reputation", data.get("reputation", "?")),
                ("Credentials Leaked", f"{'⚠ YES' if details.get('credentials_leaked') else '✓ No'}"),
                ("Data Breach", f"{'⚠ YES' if details.get('data_breach') else '✓ No'}"),
                ("Breaches Count", str(details.get("breaches", 0))),
                ("Pastes Count", str(details.get("pastes", 0))),
            ]
            _show_table("Breach Check", rows)
        else:
            console.print(f"[{C_NEON} bold]  [!] No data returned")
    except Exception as e:
        _error_box("Breach Check", str(e))
    _pause()


def tool_breach_search():
    _panel("BREACH SEARCH", "Search breach databases for compromised data")
    console.print(Text.from_markup(f"[{C_NEON} bold] ┌── Breach databases (web-based)"))
    links = [
        ("Firefox Monitor", "https://monitor.firefox.com/"),
        ("IntelX", "https://intelx.io/"),
        ("LeakPeek", "https://leakpeek.com/"),
        ("Scattered Secrets", "https://scatteredsecrets.com/"),
        ("DeHashed", "https://dehashed.com/"),
    ]
    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C_BLOOD, show_header=False)
    table.add_column("Service", style=C_GOLD, width=22)
    table.add_column("URL", style=C_WHITE)
    for name, url in links:
        table.add_row(name, f"[link={url}]{url}[/]")
    console.print(Padding(table, (1, 2)))
    console.print(Text.from_markup(f"[{C_DIM}]  Ctrl+click to open in browser[/]"))
    _pause()


# ── WEB OSINT ────────────────────────────────────────────────

_TECH_PATTERNS = [
    ("Server",            r"Server: (.+)"),
    ("X-Powered-By",      r"X-Powered-By: (.+)"),
    ("CF-Ray",            r"CF-Ray", "Cloudflare"),
    ("X-Generator",       r"X-Generator: (.+)"),
    ("X-Version",         r"X-Version: (.+)"),
    ("ASP.NET",           r"X-AspNet-Version: (.+)"),
    ("WordPress",         r"/wp-content/|/wp-admin/"),
    ("Joomla",            r"/components/|/modules/"),
    ("Drupal",            r"/sites/default/"),
    ("nginx",             r"nginx"),
    ("Apache",            r"Apache"),
    ("Node.js",           r"Node\.?[Jj]s|Express"),
    ("Python",            r"Python|Django|Flask|Werkzeug"),
    ("Ruby",              r"Ruby|Rails|Passenger"),
    ("PHP",               r"PHP|Zend"),
    ("Java",              r"Java|Tomcat|JBoss|Jetty"),
    ("Cloudflare",        r"cloudflare"),
    ("Google Cloud",      r"gws|Google frontend"),
    ("AWS",               r"AmazonS3|AWS|CloudFront"),
]


def tool_web_tech():
    _panel("WEB TECH DETECT", "Detect technologies used by a website")
    url = input(f"{_ansi(C_MID)}  URL (ex: https://example.com) >> \033[0m").strip()
    if not url: return
    if not url.startswith("http"):
        url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            headers_str = str(r.headers)
            body = r.read(1024).decode("utf-8", errors="ignore").lower()

        detected = []
        combined = headers_str.lower() + body
        for name, pattern in _TECH_PATTERNS:
            if isinstance(pattern, tuple):
                pattern = pattern[0]
            try:
                if re.search(pattern, combined, re.I):
                    detected.append(name)
            except Exception:
                pass

        rows = [("URL", url), ("Status", str(r.getcode()))]
        if detected:
            rows.append(("Technologies", ", ".join(detected)))
        else:
            rows.append(("Technologies", "None detected from headers"))
        _show_table("Web Tech Detection", rows)
    except Exception as e:
        _error_box("Web Tech", str(e))
    _pause()


def tool_web_headers():
    _panel("WEB HEADERS", "Fetch and analyze HTTP headers")
    url = input(f"{_ansi(C_MID)}  URL >> \033[0m").strip()
    if not url: return
    if not url.startswith("http"):
        url = "https://" + url
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            headers = dict(r.headers)
            rows = [(k, v) for k, v in headers.items()]
            _show_table(f"HTTP Headers — {url}", rows)
    except Exception as e:
        _error_box("Headers", str(e))
    _pause()


def tool_web_robots():
    _panel("WEB ROBOTS", "Check robots.txt of a website")
    url = input(f"{_ansi(C_MID)}  URL >> \033[0m").strip()
    if not url: return
    if not url.startswith("http"):
        url = "https://" + url
    robots_url = url.rstrip("/") + "/robots.txt"
    try:
        req = urllib.request.Request(robots_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            content = r.read().decode("utf-8", errors="ignore")
        console.print(Panel(
            content[:2000],
            title=f"[bold {C_GOLD}]robots.txt[/]",
            border_style=C_BLOOD, padding=(1, 2),
        ))
    except urllib.error.HTTPError as e:
        if e.code == 404:
            console.print(f"[{C_NEON} bold]  [!] No robots.txt found")
        else:
            _error_box("Robots", f"HTTP {e.code}")
    except Exception as e:
        _error_box("Robots", str(e))
    _pause()


# ── DORK OSINT ───────────────────────────────────────────────

DORKS = {
    "Login Pages": 'intitle:"login" | intitle:"sign in" site:{domain}',
    "Admin Panels": 'intitle:"admin" | inurl:"admin" site:{domain}',
    "Config Files": 'filetype:config | filetype:conf | filetype:ini site:{domain}',
    "Database Files": 'filetype:sql | filetype:db | filetype:mdb site:{domain}',
    "Backup Files": 'filetype:bak | filetype:backup | filetype:old site:{domain}',
    "Directory Listing": 'intitle:"index of" site:{domain}',
    "Email Addresses": '@{domain} email | @{domain} contact',
    "Error Messages": 'warning | error | fatal | exception site:{domain}',
    "Subdomains": 'site:*.{domain} -www',
    "Exposed Docs": 'filetype:pdf | filetype:xls | filetype:doc site:{domain}',
}


def tool_dork_gen():
    _panel("DORK GENERATOR", "Generate Google dorks for OSINT")
    domain = input(f"{_ansi(C_MID)}  Target domain >> \033[0m").strip()
    if not domain: return
    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C_BLOOD, show_header=True)
    table.add_column("#", style=C_DIM, width=4)
    table.add_column("Type", style=C_GOLD, width=18)
    table.add_column("Dork", style=C_WHITE)
    for i, (dork_type, dork) in enumerate(DORKS.items(), 1):
        dork_str = dork.format(domain=domain)
        table.add_row(str(i), dork_type, dork_str)
    console.print(Padding(table, (1, 2)))
    idx = input(f"\n{_ansi(C_MID)}  Open dork # (or Enter to skip) >> \033[0m").strip()
    if idx and idx.isdigit():
        i = int(idx) - 1
        if 0 <= i < len(DORKS):
            dork = list(DORKS.values())[i].format(domain=domain)
            url = f"https://google.com/search?q={urllib.parse.quote(dork)}"
            console.print(Text.from_markup(f"\n[{C_GOLD}]  Dork URL:[/] [link={url}]{url}[/]"))
            console.print(Text.from_markup(f"[{C_DIM}]  Ctrl+click to open[/]"))
    _pause()


def tool_dork_search():
    _panel("DORK SEARCH", "Quick dork searches for common OSINT targets")
    query = input(f"{_ansi(C_MID)}  Search term >> \033[0m").strip()
    if not query: return
    links = [
        ("Google", f"https://google.com/search?q={urllib.parse.quote(query)}"),
        ("Bing", f"https://bing.com/search?q={urllib.parse.quote(query)}"),
        ("Yandex", f"https://yandex.com/search/?text={urllib.parse.quote(query)}"),
        ("DuckDuckGo", f"https://duckduckgo.com/?q={urllib.parse.quote(query)}"),
    ]
    table = Table(box=box.MINIMAL_DOUBLE_HEAD, border_style=C_BLOOD, show_header=False)
    table.add_column("Engine", style=C_GOLD, width=14)
    table.add_column("URL", style=C_WHITE)
    for name, url in links:
        table.add_row(name, f"[link={url}]{url}[/]")
    console.print(Padding(table, (1, 2)))
    console.print(Text.from_markup(f"[{C_DIM}]  Ctrl+click to open in browser[/]"))
    _pause()


# ── IMAGE OSINT ──────────────────────────────────────────────

def tool_exif_viewer():
    _panel("EXIF VIEWER", "View EXIF metadata from an image file")
    path = input(f"{_ansi(C_MID)}  Image path >> \033[0m").strip().strip('"')
    if not path or not os.path.isfile(path):
        _error_box("File", f"File not found: {path}")
        _pause()
        return
    try:
        from PIL import Image
        from PIL.ExifTags import TAGS
        img = Image.open(path)
        exif = img._getexif()
        if exif:
            rows = []
            for tag_id, value in exif.items():
                tag = TAGS.get(tag_id, tag_id)
                rows.append((str(tag), str(value)[:80]))
            _show_table(f"EXIF Data — {os.path.basename(path)}", rows)
        else:
            console.print(f"[{C_NEON} bold]  [!] No EXIF data found")
    except ImportError:
        _error_box("Missing dep", "Install Pillow: pip install Pillow")
    except Exception as e:
        _error_box("EXIF", str(e))
    _pause()


def tool_image_meta():
    _panel("IMAGE METADATA", "Extract basic image metadata")
    path = input(f"{_ansi(C_MID)}  Image path >> \033[0m").strip().strip('"')
    if not path or not os.path.isfile(path):
        _error_box("File", f"File not found: {path}")
        _pause()
        return
    try:
        from PIL import Image
        img = Image.open(path)
        rows = [
            ("Filename", os.path.basename(path)),
            ("Size", f"{img.width} x {img.height} px"),
            ("Format", img.format or "Unknown"),
            ("Mode", img.mode),
        ]
        _show_table("Image Metadata", rows)
    except ImportError:
        _error_box("Missing dep", "Install Pillow: pip install Pillow")
    except Exception as e:
        _error_box("Metadata", str(e))
    _pause()
