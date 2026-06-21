"""Email Intelligence — wrapper for holehe."""
import json
import subprocess

from core.engine import ScanResult


class EmailScanner:
    def check_reputation(self, email):
        try:
            proc = subprocess.run(
                ["holehe", "--only-used", "--no-color", "--no-clear", email],
                capture_output=True, text=True, timeout=30
            )
            output = proc.stdout
            found = []
            for line in output.split("\n"):
                line = line.strip()
                if "[+]" in line:
                    site = line.split("[+]")[-1].strip()
                    if site and site != "Email used":
                        found.append(site)
            return ScanResult(
                source="Holehe",
                category="email_enum",
                status="found" if found else "none",
                data={"services": found, "count": len(found)},
            )
        except FileNotFoundError:
            return ScanResult(source="Holehe", category="email_enum", status="error", error="holehe not installed: pip install holehe")
        except Exception as e:
            return ScanResult(source="Holehe", category="email_enum", status="error", error=str(e))

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

    def discover_accounts(self, email):
        username = email.split("@")[0]
        sites = [
            ("GitHub", f"https://github.com/{username}"),
            ("Twitter/X", f"https://x.com/{username}"),
            ("Reddit", f"https://reddit.com/user/{username}"),
            ("Instagram", f"https://instagram.com/{username}"),
            ("TikTok", f"https://tiktok.com/@{username}"),
            ("YouTube", f"https://youtube.com/@{username}"),
        ]
        import urllib.request
        found = []
        for name, url in sites:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    if r.getcode() == 200:
                        body = r.read(1000).decode("utf-8", errors="ignore").lower()
                        if "not found" not in body and "does not exist" not in body:
                            found.append({"service": name, "url": url})
            except Exception:
                pass
        return ScanResult(
            source="Account Discovery",
            category="accounts",
            status="found" if found else "none",
            data={"accounts": found, "count": len(found)},
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

    def generate_dorks(self, email):
        username = email.split("@")[0]
        domain = email.split("@")[1] if "@" in email else ""
        dorks = [
            f'"{email}"',
            f'"{username}" site:linkedin.com',
            f'"{username}" site:github.com',
            f'filetype:pdf "{email}"',
        ]
        if domain:
            dorks.append(f'"@{domain}" email contact')
        import urllib.parse
        dork_url = f"https://google.com/search?q={urllib.parse.quote(" | ".join(dorks))}"
        return ScanResult(
            source="Google Dorks",
            category="dorks",
            status="found",
            data={"dorks": dorks},
            url=dork_url,
        )
