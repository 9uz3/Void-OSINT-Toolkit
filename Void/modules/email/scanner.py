"""Email Intelligence — wrapper for user-scanner."""
import json
import subprocess

from core.engine import ScanResult


class EmailScanner:
    def check_reputation(self, email):
        try:
            proc = subprocess.run(
                ["user-scanner", "-e", email, "--only-found", "-f", "json"],
                capture_output=True, text=True, timeout=120
            )
            output = proc.stdout
            results = []
            try:
                data = json.loads(output)
                for item in data:
                    if item.get("status") == "Registered":
                        results.append({
                            "service": item.get("site_name", "?"),
                            "url": item.get("url", ""),
                            "category": item.get("category", ""),
                        })
            except json.JSONDecodeError:
                for line in output.split("\n"):
                    line = line.strip()
                    if "[✔]" in line and "Registered" in line:
                        parts = line.split("[✔]")
                        if len(parts) > 1:
                            site = parts[1].split("(")[0].strip()
                            results.append({"service": site, "url": "", "category": ""})

            return ScanResult(
                source="user-scanner",
                category="email_enum",
                status="found" if results else "none",
                data={"services": results, "count": len(results)},
            )
        except FileNotFoundError:
            return ScanResult(source="user-scanner", category="email_enum", status="error", error="user-scanner not installed: pip install user-scanner")
        except Exception as e:
            return ScanResult(source="user-scanner", category="email_enum", status="error", error=str(e))

    def check_breaches(self, email):
        try:
            proc = subprocess.run(
                ["h8mail", "-t", email, "-o", "/dev/null", "--json"],
                capture_output=True, text=True, timeout=30
            )
            output = proc.stdout
            breaches = []
            for line in output.split("\n"):
                if "Breach" in line or "breach" in line:
                    breaches.append(line.strip())
            return ScanResult(
                source="h8mail",
                category="breach",
                status="found" if breaches else "none",
                data={"breaches": breaches, "count": len(breaches)},
            )
        except FileNotFoundError:
            return ScanResult(source="h8mail", category="breach", status="error", error="h8mail not installed: pip install h8mail")
        except Exception as e:
            return ScanResult(source="h8mail", category="breach", status="error", error=str(e))

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
                return ScanResult(
                    source="Gravatar",
                    category="profile",
                    status="found",
                    data={"display_name": display, "profile_url": profile_url, "urls": urls},
                    url=profile_url or f"https://gravatar.com/{email_hash}",
                )
            return ScanResult(source="Gravatar", category="profile", status="none")
        except Exception:
            return ScanResult(source="Gravatar", category="profile", status="none")
