"""Email Intelligence — real OSINT tools."""
import hashlib
import json
import subprocess
import urllib.parse
import urllib.request

from core.engine import ScanResult


class EmailScanner:
    def check_reputation(self, email):
        try:
            url = f"https://emailrep.io/{urllib.parse.quote(email)}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
                "Accept": "application/json",
            })
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
            if "email" in data:
                details = data.get("details", {})
                return ScanResult(
                    source="EmailRep",
                    category="reputation",
                    status="found",
                    data={
                        "reputation": data.get("reputation", "unknown"),
                        "suspicious": str(data.get("suspicious", False)),
                        "credentials_leaked": str(details.get("credentials_leaked", False)),
                        "data_breach": str(details.get("data_breach", False)),
                        "malicious_activity": str(details.get("malicious_activity", False)),
                        "spam": str(details.get("spam", False)),
                        "free_provider": str(details.get("free_provider", False)),
                        "deliverable": str(details.get("deliverable", False)),
                        "profiles": ", ".join(details.get("profiles", [])),
                    },
                    url=url,
                )
        except urllib.error.HTTPError as e:
            return ScanResult(source="EmailRep", category="reputation", status="error", error=f"HTTP {e.code} — API key required for full access")
        except Exception as e:
            return ScanResult(source="EmailRep", category="reputation", status="error", error=str(e))

    def check_breaches(self, email):
        try:
            proc = subprocess.run(
                ["holehe", "--only-used", "--no-color", email],
                capture_output=True, text=True, timeout=30
            )
            output = proc.stdout
            found = []
            for line in output.split("\n"):
                line = line.strip()
                if "[+]" in line:
                    site = line.split("[+]")[-1].strip()
                    if site:
                        found.append(site)
            if found:
                return ScanResult(
                    source="Holehe",
                    category="breach",
                    status="found",
                    data={"breached_sites": ", ".join(found), "count": str(len(found))},
                    url=f"https://haveibeenpwned.com/account/{urllib.parse.quote(email)}",
                )
            return ScanResult(source="Holehe", category="breach", status="none", data={"count": "0"})
        except Exception as e:
            return ScanResult(source="Holehe", category="breach", status="error", error=str(e))

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
        found = []
        for name, url in sites:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    code = r.getcode()
                    if code == 200:
                        body = r.read(2000).decode("utf-8", errors="ignore")
                        if "not found" not in body.lower() and "does not exist" not in body.lower():
                            found.append(f"{name}: {url}")
            except Exception:
                pass
        return ScanResult(
            source="Account Discovery",
            category="accounts",
            status="found" if found else "none",
            data={"accounts": ", ".join(found) if found else "none found", "count": str(len(found))},
        )

    def check_gravatar(self, email):
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
                result_data = {"display_name": display}
                if profile_url:
                    result_data["profile_url"] = profile_url
                if urls:
                    result_data["urls"] = ", ".join(urls[:5])
                return ScanResult(
                    source="Gravatar",
                    category="profile",
                    status="found",
                    data=result_data,
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
        dork_url = f"https://google.com/search?q={urllib.parse.quote(' | '.join(dorks))}"
        return ScanResult(
            source="Google Dorks",
            category="dorks",
            status="found",
            data={"dorks": " | ".join(dorks)},
            url=dork_url,
        )
