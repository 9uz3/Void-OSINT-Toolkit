"""Username Intelligence — wrapper for sherlock + maigret + ghunt + nexfil."""
import json
import subprocess

from core.engine import ScanResult


class UsernameScanner:
    def sherlock_scan(self, username):
        try:
            proc = subprocess.run(
                ["sherlock", username, "--timeout", "5", "--print-found", "--json", "-"],
                capture_output=True, text=True, timeout=60
            )
            output = proc.stdout
            found = []
            for line in output.split("\n"):
                line = line.strip()
                if "[+" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        site = parts[0].replace("[+]", "").replace("[", "").replace("]", "").strip()
                        url = parts[1].strip()
                        if site and url:
                            found.append({"service": site, "url": url})
            return ScanResult(
                source="Sherlock",
                category="platforms",
                status="found" if found else "none",
                data={"profiles": found, "count": len(found)},
            )
        except FileNotFoundError:
            return ScanResult(source="Sherlock", category="platforms", status="error", error="sherlock not installed: pip install sherlock-project")
        except Exception as e:
            return ScanResult(source="Sherlock", category="platforms", status="error", error=str(e))

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
                for line in output.split("\n"):
                    if "http" in line.lower() and ("found" in line.lower() or "+" in line):
                        found.append({"service": line.split()[0] if line.split() else "?", "url": line.strip()})
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
            proc = subprocess.run(
                ["nexfil", "-q", "-L", "50", username],
                capture_output=True, text=True, timeout=60
            )
            output = proc.stdout
            found = []
            for line in output.split("\n"):
                line = line.strip()
                if "[+]" in line:
                    parts = line.split("[+]", 1)
                    if len(parts) == 2:
                        site = parts[1].strip()
                        if site:
                            found.append({"service": site.split(":")[0] if ":" in site else site, "url": site})
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
