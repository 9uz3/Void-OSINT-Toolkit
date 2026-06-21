"""Username Intelligence — wrapper for user-scanner with live feedback."""
import json
import subprocess
import sys
import threading
import time

from core.engine import ScanResult
from lib.void_common import console
from lib import constants as C

_SPIN = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]


def _spinner(stop_event, msg="Scanning"):
    i = 0
    while not stop_event.is_set():
        char = _SPIN[i % len(_SPIN)]
        sys.stdout.write(f"\r    {char} {msg}...")
        sys.stdout.flush()
        i += 1
        time.sleep(0.1)
    sys.stdout.write("\r" + " " * 50 + "\r")
    sys.stdout.flush()


class UsernameScanner:
    def sherlock_scan(self, username):
        results = []
        stop = threading.Event()
        t = threading.Thread(target=_spinner, args=(stop, "user-scanner scanning"))
        t.daemon = True
        t.start()

        try:
            proc = subprocess.Popen(
                ["user-scanner", "-u", username, "--only-found"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            for line in proc.stdout:
                line = line.strip()
                if "[✔]" in line:
                    parts = line.split("[✔]")
                    if len(parts) > 1:
                        site_part = parts[1].split("(")[0].strip()
                        site = site_part.split(":")[0].strip() if ":" in site_part else site_part
                        if site:
                            results.append({"service": site, "url": "", "category": ""})
            proc.wait(timeout=120)
        except FileNotFoundError:
            stop.set()
            t.join(timeout=1)
            return ScanResult(source="user-scanner", category="platforms", status="error", error="user-scanner not installed: pip install user-scanner")
        except subprocess.TimeoutExpired:
            proc.kill()
        except Exception as e:
            stop.set()
            t.join(timeout=1)
            return ScanResult(source="user-scanner", category="platforms", status="error", error=str(e))

        stop.set()
        t.join(timeout=1)

        if results:
            console.print(f"    [{C.C_NEON}]✔[/] [{C.C_GOLD}]{len(results)}[/] profiles found:")
            for r in results:
                console.print(f"      [{C.C_NEON}]→[/] [{C.C_WHITE}]{r['service']}[/]")
        else:
            console.print(f"    [{C.C_DIM}]○ No profiles found[/]")

        return ScanResult(
            source="user-scanner",
            category="platforms",
            status="found" if results else "none",
            data={"profiles": results, "count": len(results)},
        )

    def maigret_scan(self, username):
        try:
            proc = subprocess.run(
                ["maigret", username, "--json", "-o", "/dev/stdout"],
                capture_output=True, text=True, timeout=90
            )
            output = proc.stdout
            found = []
            try:
                data = json.loads(output)
                for site, info in data.items():
                    if isinstance(info, dict) and info.get("url_user"):
                        found.append({"service": site, "url": info["url_user"]})
            except json.JSONDecodeError:
                pass
            return ScanResult(
                source="Maigret",
                category="platforms",
                status="found" if found else "none",
                data={"profiles": found, "count": len(found)},
            )
        except FileNotFoundError:
            return ScanResult(source="Maigret", category="platforms", status="error", error="maigret not installed: pip install maigret")
        except Exception as e:
            return ScanResult(source="Maigret", category="platforms", status="error", error=str(e))

    def social_check(self, username):
        import urllib.parse
        links = [
            {"service": "Google", "url": f"https://google.com/search?q={urllib.parse.quote(username)}"},
            {"service": "Twitter", "url": f"https://twitter.com/search?q={urllib.parse.quote(username)}"},
            {"service": "Reddit", "url": f"https://reddit.com/search?q={urllib.parse.quote(username)}"},
        ]
        return ScanResult(
            source="Social Search",
            category="social",
            status="found",
            data={"search_links": links, "count": len(links)},
        )

    def nexfil_scan(self, username):
        try:
            proc = subprocess.Popen(
                ["nexfil", "-q", "-L", "50", username],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            found = []
            for line in proc.stdout:
                line = line.strip()
                if "[+]" in line:
                    parts = line.split("[+]", 1)
                    if len(parts) == 2:
                        site = parts[1].strip()
                        if site:
                            found.append({"service": site.split(":")[0] if ":" in site else site, "url": site})
            proc.wait(timeout=60)
            return ScanResult(
                source="Nexfil",
                category="email_by_username",
                status="found" if found else "none",
                data={"emails": found, "count": len(found)},
            )
        except FileNotFoundError:
            return ScanResult(source="Nexfil", category="email_by_username", status="error", error="nexfil not installed: pip install nexfil")
        except Exception as e:
            return ScanResult(source="Nexfil", category="email_by_username", status="error", error=str(e))
