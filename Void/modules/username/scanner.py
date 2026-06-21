"""Username Intelligence — wrapper for user-scanner with real-time output."""
import json
import subprocess

from core.engine import ScanResult
from lib.void_common import console
from lib import constants as C


class UsernameScanner:
    def sherlock_scan(self, username):
        results = []
        try:
            proc = subprocess.Popen(
                ["user-scanner", "-u", username, "--only-found"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            current_category = ""
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                if line.startswith("==") and "==" in line[2:]:
                    cat = line.replace("=", "").strip()
                    if cat and cat != current_category:
                        current_category = cat
                        console.print(f"    [{C.C_DIM}]─── {cat} ───[/]")
                elif "[✔]" in line:
                    parts = line.split("[✔]")
                    if len(parts) > 1:
                        site_part = parts[1].split("(")[0].strip()
                        site = site_part.split(":")[0].strip() if ":" in site_part else site_part
                        if site:
                            results.append({"service": site, "url": "", "category": current_category})
                            console.print(f"    [{C.C_NEON}]→[/] [{C.C_GOLD}]{site}[/]")
            proc.wait(timeout=120)
            return ScanResult(
                source="user-scanner",
                category="platforms",
                status="found" if results else "none",
                data={"profiles": results, "count": len(results)},
            )
        except FileNotFoundError:
            return ScanResult(source="user-scanner", category="platforms", status="error", error="user-scanner not installed: pip install user-scanner")
        except subprocess.TimeoutExpired:
            proc.kill()
            return ScanResult(
                source="user-scanner",
                category="platforms",
                status="found" if results else "none",
                data={"profiles": results, "count": len(results)},
            )
        except Exception as e:
            return ScanResult(source="user-scanner", category="platforms", status="error", error=str(e))

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
                            console.print(f"    [{C.C_NEON}]→[/] [{C.C_GOLD}]{site}[/]")
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
