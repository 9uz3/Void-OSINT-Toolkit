"""Email Intelligence — scanner module."""
import json
import urllib.parse
import urllib.request

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Void.core.engine import ScanResult


class EmailScanner:
    def check_reputation(self, email):
        try:
            url = f"https://emailrep.io/{urllib.parse.quote(email)}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
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
                        "suspicious": data.get("suspicious", False),
                        "credentials_leaked": details.get("credentials_leaked", False),
                        "data_breach": details.get("data_breach", False),
                        "malicious_activity": details.get("malicious_activity", False),
                        "spam": details.get("spam", False),
                        "free_provider": details.get("free_provider", False),
                        "deliverable": details.get("deliverable", False),
                        "profiles": ", ".join(details.get("profiles", [])),
                    },
                    url=url,
                )
        except Exception as e:
            return ScanResult(source="EmailRep", category="reputation", status="error", error=str(e))

    def check_breaches(self, email):
        try:
            url = f"https://haveibeenpwned.com/unifiedsearch/{urllib.parse.quote(email)}"
            req = urllib.request.Request(url, headers={
                "User-Agent": "Mozilla/5.0",
                "hibp-api-key": "",
            })
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
            breaches = data.get("Breaches", [])
            pastes = data.get("Pastes", [])
            return ScanResult(
                source="HaveIBeenPwned",
                category="breach",
                status="found" if breaches or pastes else "none",
                data={
                    "breaches_count": len(breaches),
                    "pastes_count": len(pastes),
                    "breach_names": ", ".join(b.get("Name", "") for b in breaches[:10]),
                },
                url=f"https://haveibeenpwned.com/account/{urllib.parse.quote(email)}",
            )
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return ScanResult(source="HaveIBeenPwned", category="breach", status="none", data={"breaches_count": 0})
            return ScanResult(source="HaveIBeenPwned", category="breach", status="error", error=f"HTTP {e.code}")
        except Exception as e:
            return ScanResult(source="HaveIBeenPwned", category="breach", status="error", error=str(e))

    def discover_accounts(self, email):
        username = email.split("@")[0]
        sites = [
            ("GitHub", f"https://github.com/{username}"),
            ("Twitter/X", f"https://x.com/{username}"),
            ("Reddit", f"https://reddit.com/user/{username}"),
        ]
        found = []
        for name, url in sites:
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    if r.getcode() == 200:
                        found.append(name)
            except Exception:
                pass
        return ScanResult(
            source="Holehe",
            category="accounts",
            status="found" if found else "none",
            data={"associated_accounts": ", ".join(found) if found else "none found"},
        )

    def check_gravatar(self, email):
        import hashlib
        email_hash = hashlib.md5(email.lower().strip().encode()).hexdigest()
        url = f"https://gravatar.com/{email_hash}.json"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read().decode())
            entry = data.get("entry", [{}])[0]
            display = entry.get("displayName", "")
            urls = [u.get("value", "") for u in entry.get("urls", [])]
            return ScanResult(
                source="Gravatar",
                category="profile",
                status="found" if display else "none",
                data={
                    "display_name": display,
                    "profile_url": entry.get("profileUrl", ""),
                    "urls": ", ".join(urls[:5]),
                },
                url=f"https://gravatar.com/{email_hash}",
            )
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
        return ScanResult(
            source="Google Dorks",
            category="dorks",
            status="found",
            data={"dorks": " | ".join(dorks)},
            url=f"https://google.com/search?q={urllib.parse.quote(' | '.join(dorks))}",
        )
