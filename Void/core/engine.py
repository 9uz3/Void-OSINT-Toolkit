"""OSINT Engine — core orchestration layer.

Receives user input, selects tools, executes modules, normalizes results, generates reports.
"""
import json
import os
import time
from datetime import datetime

from rich.text import Text
from rich.table import Table
from rich.panel import Panel
from rich.padding import Padding
from rich import box

from lib import constants as C
from lib.void_common import console, error_box, ansi_hex


class ScanResult:
    def __init__(self, source, category, status, data=None, url="", error=None):
        self.source = source
        self.category = category
        self.status = status
        self.data = data or {}
        self.url = url
        self.error = error
        self.timestamp = datetime.now().isoformat()

    def is_success(self):
        return self.status == "found" and self.error is None

    def to_dict(self):
        return {
            "source": self.source,
            "category": self.category,
            "status": self.status,
            "data": self.data,
            "url": self.url,
            "error": self.error,
            "timestamp": self.timestamp,
        }


class OSINTEngine:
    def __init__(self):
        self.results = []
        self.target = ""
        self.scan_type = ""
        self.start_time = None
        self.end_time = None

    def _sys_msg(self, tag, message, color=None):
        if color is None:
            color = C.C_NEON
        console.print(Text.from_markup(
            f"[{C.C_DIM}][[/][{color} bold]{tag}[/][{C.C_DIM}]][/] {message}"
        ))

    def _exec_header(self, title, target):
        W = 56
        header = (
            f"[{C.C_BLOOD}]╔{'═' * W}╗[/]\n"
            f"[{C.C_BLOOD}]║[/]  [{C.C_NEON}]VOID OSINT ENGINE[/]{' ' * (W - 19)}[{C.C_BLOOD}]║[/]\n"
            f"[{C.C_BLOOD}]║[/]  [{C.C_GOLD}]{title}[/]{' ' * max(0, W - 2 - len(title))}[{C.C_BLOOD}]║[/]\n"
            f"[{C.C_BLOOD}]╚{'═' * W}╝[/]"
        )
        console.print(Text.from_markup(header))
        console.print()
        console.print(Text.from_markup(f"  [{C.C_GOLD}]TARGET:[/]  [{C.C_WHITE}]{target}[/]"))
        console.print()

    def _step(self, number, total, label, status="running"):
        icons = {"done": f"[{C.C_NEON}]✓[/]", "running": f"[{C.C_GOLD}]>[/]", "pending": f"[{C.C_DIM}][ ][/]", "error": f"[#FF4444]✗[/]"}
        icon = icons.get(status, icons["pending"])
        console.print(f"  {icon}  [{C.C_DIM}]{number}/{total}[/] {label}")

    def _progress_bar(self, current, total, width=30):
        pct = current / total if total > 0 else 0
        filled = int(width * pct)
        bar = f"[{C.C_NEON}]{'█' * filled}[/{C.C_DIM}]{'░' * (width - filled)}[/]"
        console.print(f"\r  [{C.C_GOLD}]{current}/{total}[/] {bar} [{C.C_WHITE}]{int(pct*100)}%[/]", end="")

    def run_email_scan(self, email):
        from modules.email.scanner import EmailScanner
        self.target = email
        self.scan_type = "email"
        self.start_time = time.time()
        self.results = []

        self._exec_header("EMAIL INTELLIGENCE", email)
        self._sys_msg("SYSTEM", "Initializing email investigation...")

        scanner = EmailScanner()
        steps = [
            ("EmailRep reputation check", scanner.check_reputation),
            ("HaveIBeenPwned breach scan", scanner.check_breaches),
            ("Holehe account discovery", scanner.discover_accounts),
            ("Gravatar profile lookup", scanner.check_gravatar),
            ("Google Dork generation", scanner.generate_dorks),
        ]

        total = len(steps)
        for i, (label, func) in enumerate(steps, 1):
            self._step(i, total, label, "running")
            try:
                result = func(email)
                if result:
                    self.results.append(result)
                self._step(i, total, label, "done")
            except Exception as e:
                self._step(i, total, label, "error")
                self.results.append(ScanResult(
                    source=label.split(" ")[0], category="email",
                    status="error", error=str(e)
                ))

        self.end_time = time.time()
        self._sys_msg("SUCCESS", f"Investigation complete — {len(self.results)} checks performed")
        return self.results

    def run_username_scan(self, username):
        from modules.username.scanner import UsernameScanner
        self.target = username
        self.scan_type = "username"
        self.start_time = time.time()
        self.results = []

        self._exec_header("USERNAME INTELLIGENCE", username)
        self._sys_msg("SYSTEM", "Initializing username investigation...")

        scanner = UsernameScanner()
        steps = [
            ("Sherlock platform scan", scanner.sherlock_scan),
            ("Maigret cross-platform check", scanner.maigret_scan),
            ("WhatsMyName web search", scanner.whatsmyname_scan),
            ("Social media presence check", scanner.social_check),
        ]

        total = len(steps)
        for i, (label, func) in enumerate(steps, 1):
            self._step(i, total, label, "running")
            try:
                result = func(username)
                if result:
                    self.results.extend(result if isinstance(result, list) else [result])
                self._step(i, total, label, "done")
            except Exception as e:
                self._step(i, total, label, "error")
                self.results.append(ScanResult(
                    source=label.split(" ")[0], category="username",
                    status="error", error=str(e)
                ))

        self.end_time = time.time()
        self._sys_msg("SUCCESS", f"Investigation complete — {len(self.results)} checks performed")
        return self.results

    def run_phone_scan(self, phone):
        from modules.phone.scanner import PhoneScanner
        self.target = phone
        self.scan_type = "phone"
        self.start_time = time.time()
        self.results = []

        self._exec_header("PHONE INTELLIGENCE", phone)
        self._sys_msg("SYSTEM", "Initializing phone investigation...")

        scanner = PhoneScanner()
        steps = [
            ("Number validation & parsing", scanner.validate_number),
            ("Carrier identification", scanner.identify_carrier),
            ("Geolocation lookup", scanner.geolocate),
            ("Risk assessment", scanner.assess_risk),
        ]

        total = len(steps)
        for i, (label, func) in enumerate(steps, 1):
            self._step(i, total, label, "running")
            try:
                result = func(phone)
                if result:
                    self.results.append(result)
                self._step(i, total, label, "done")
            except Exception as e:
                self._step(i, total, label, "error")
                self.results.append(ScanResult(
                    source=label.split(" ")[0], category="phone",
                    status="error", error=str(e)
                ))

        self.end_time = time.time()
        self._sys_msg("SUCCESS", f"Investigation complete — {len(self.results)} checks performed")
        return self.results

    def run_ip_scan(self, ip):
        from modules.ip.scanner import IPScanner
        self.target = ip
        self.scan_type = "ip"
        self.start_time = time.time()
        self.results = []

        self._exec_header("IP INTELLIGENCE", ip)
        self._sys_msg("SYSTEM", "Initializing IP investigation...")

        scanner = IPScanner()
        steps = [
            ("Geolocation lookup", scanner.geolocate),
            ("VPN/Proxy detection", scanner.detect_vpn),
            ("WHOIS lookup", scanner.whois_lookup),
            ("Port scan (common)", scanner.common_ports),
        ]

        total = len(steps)
        for i, (label, func) in enumerate(steps, 1):
            self._step(i, total, label, "running")
            try:
                result = func(ip)
                if result:
                    self.results.append(result)
                self._step(i, total, label, "done")
            except Exception as e:
                self._step(i, total, label, "error")
                self.results.append(ScanResult(
                    source=label.split(" ")[0], category="ip",
                    status="error", error=str(e)
                ))

        self.end_time = time.time()
        self._sys_msg("SUCCESS", f"Investigation complete — {len(self.results)} checks performed")
        return self.results

    def run_domain_scan(self, domain):
        from modules.domain.scanner import DomainScanner
        self.target = domain
        self.scan_type = "domain"
        self.start_time = time.time()
        self.results = []

        self._exec_header("DOMAIN INTELLIGENCE", domain)
        self._sys_msg("SYSTEM", "Initializing domain investigation...")

        scanner = DomainScanner()
        steps = [
            ("WHOIS lookup", scanner.whois_lookup),
            ("DNS records", scanner.dns_records),
            ("SSL certificate", scanner.ssl_check),
            ("Subdomain enumeration", scanner.enumerate_subdomains),
            ("Web technology detection", scanner.detect_tech),
        ]

        total = len(steps)
        for i, (label, func) in enumerate(steps, 1):
            self._step(i, total, label, "running")
            try:
                result = func(domain)
                if result:
                    self.results.append(result)
                self._step(i, total, label, "done")
            except Exception as e:
                self._step(i, total, label, "error")
                self.results.append(ScanResult(
                    source=label.split(" ")[0], category="domain",
                    status="error", error=str(e)
                ))

        self.end_time = time.time()
        self._sys_msg("SUCCESS", f"Investigation complete — {len(self.results)} checks performed")
        return self.results

    def show_results(self):
        from modules.report import show_results_panel
        show_results_panel(self)

    def save_reports(self):
        from modules.report import save_all_reports
        return save_all_reports(self)
