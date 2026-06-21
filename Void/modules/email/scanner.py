"""Email Intelligence — wrapper for user-scanner with live feedback."""
import json
import os
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


class EmailScanner:
    def check_reputation(self, email):
        results = []
        stop = threading.Event()
        t = threading.Thread(target=_spinner, args=(stop, "user-scanner scanning"))
        t.daemon = True
        t.start()

        try:
            proc = subprocess.Popen(
                ["user-scanner", "-e", email, "--only-found"],
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
            return ScanResult(source="user-scanner", category="email_enum", status="error", error="user-scanner not installed: pip install user-scanner")
        except subprocess.TimeoutExpired:
            proc.kill()
        except Exception as e:
            stop.set()
            t.join(timeout=1)
            return ScanResult(source="user-scanner", category="email_enum", status="error", error=str(e))

        stop.set()
        t.join(timeout=1)

        if results:
            console.print(f"    [{C.C_NEON}]✔[/] [{C.C_GOLD}]{len(results)}[/] accounts found:")
            for r in results:
                console.print(f"      [{C.C_NEON}]→[/] [{C.C_WHITE}]{r['service']}[/]")
        else:
            console.print(f"    [{C.C_DIM}]○ No accounts found[/]")

        return ScanResult(
            source="user-scanner",
            category="email_enum",
            status="found" if results else "none",
            data={"services": results, "count": len(results)},
        )

    def check_breaches(self, email):
        results = []
        stop = threading.Event()
        t = threading.Thread(target=_spinner, args=(stop, "h8mail breach check"))
        t.daemon = True
        t.start()

        try:
            proc = subprocess.Popen(
                ["h8mail", "-t", email, "-o", "NUL" if os.name == "nt" else "/dev/null", "--json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            output, _ = proc.communicate(timeout=30)
            for line in output.split("\n"):
                if "Breach" in line or "breach" in line:
                    results.append(line.strip())
        except FileNotFoundError:
            stop.set()
            t.join(timeout=1)
            return ScanResult(source="h8mail", category="breach", status="error", error="h8mail not installed: pip install h8mail")
        except subprocess.TimeoutExpired:
            pass
        except Exception as e:
            stop.set()
            t.join(timeout=1)
            return ScanResult(source="h8mail", category="breach", status="error", error=str(e))

        stop.set()
        t.join(timeout=1)

        if results:
            console.print(f"    [{C.C_NEON}]✔[/] [{C.C_GOLD}]{len(results)}[/] breaches found")
        else:
            console.print(f"    [{C.C_DIM}]○ No breaches found[/]")

        return ScanResult(
            source="h8mail",
            category="breach",
            status="found" if results else "none",
            data={"breaches": results, "count": len(results)},
        )

    def check_gravatar(self, email):
        import hashlib
        import urllib.request
        email_hash = hashlib.md5(email.lower().strip().encode()).hexdigest()
        url = f"https://gravatar.com/{email_hash}.json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read().decode())
            entry = data.get("entry", [{}])[0]
            display = entry.get("displayName", "")
            profile_url = entry.get("profileUrl", "")
            urls = [u.get("value", "") for u in entry.get("urls", [])]
            if display or profile_url:
                console.print(f"    [{C.C_NEON}]✔[/] [{C.C_GOLD}]Gravatar[/] profile found")
                return ScanResult(
                    source="Gravatar",
                    category="profile",
                    status="found",
                    data={"display_name": display, "profile_url": profile_url, "urls": urls},
                    url=profile_url or f"https://gravatar.com/{email_hash}",
                )
            console.print(f"    [{C.C_DIM}]○ No Gravatar profile[/]")
            return ScanResult(source="Gravatar", category="profile", status="none")
        except Exception:
            console.print(f"    [{C.C_DIM}]○ No Gravatar profile[/]")
            return ScanResult(source="Gravatar", category="profile", status="none")
