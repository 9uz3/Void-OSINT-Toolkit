"""Username Intelligence — real OSINT tools."""
import json
import subprocess
import urllib.parse
import urllib.request
import urllib.error

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
                if line.startswith("[+") or "Claimed:" in line:
                    parts = line.split(":", 1)
                    if len(parts) == 2:
                        site = parts[0].replace("[+]", "").strip()
                        url = parts[1].strip()
                        if site and url:
                            found.append(f"{site}: {url}")
            if found:
                return ScanResult(
                    source="Sherlock",
                    category="platforms",
                    status="found",
                    data={"found_profiles": "\n".join(found), "count": str(len(found))},
                )
            return ScanResult(source="Sherlock", category="platforms", status="none", data={"count": "0"})
        except FileNotFoundError:
            return ScanResult(source="Sherlock", category="platforms", status="error", error="sherlock not installed")
        except Exception as e:
            return ScanResult(source="Sherlock", category="platforms", status="error", error=str(e))

    def maigret_scan(self, username):
        sites = [
            ("GitHub", "https://github.com/{u}"),
            ("Twitter/X", "https://x.com/{u}"),
            ("Reddit", "https://reddit.com/user/{u}"),
            ("Instagram", "https://instagram.com/{u}"),
            ("Twitch", "https://twitch.tv/{u}"),
            ("YouTube", "https://youtube.com/@{u}"),
            ("Telegram", "https://t.me/{u}"),
            ("Medium", "https://medium.com/@{u}"),
            ("Pinterest", "https://pinterest.com/{u}"),
            ("TikTok", "https://tiktok.com/@{u}"),
        ]
        found = []
        for name, url_template in sites:
            url = url_template.format(u=username)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    if r.getcode() == 200:
                        body = r.read(1000).decode("utf-8", errors="ignore").lower()
                        if "not found" not in body and "does not exist" not in body and "no user" not in body:
                            found.append(f"{name}: {url}")
            except Exception:
                pass
        return ScanResult(
            source="Maigret",
            category="platforms",
            status="found" if found else "none",
            data={"found_profiles": "\n".join(found) if found else "none found", "count": str(len(found))},
        )

    def whatsmyname_scan(self, username):
        sites = [
            ("GitHub", "https://github.com/{u}"),
            ("GitLab", "https://gitlab.com/{u}"),
            ("Bitbucket", "https://bitbucket.org/{u}/"),
            ("Dev.to", "https://dev.to/{u}"),
            ("HackerRank", "https://hackerrank.com/{u}"),
            ("LeetCode", "https://leetcode.com/{u}"),
            ("Replit", "https://replit.com/@{u}"),
            ("Keybase", "https://keybase.io/{u}"),
            ("Steam", "https://steamcommunity.com/id/{u}"),
        ]
        found = []
        for name, url_template in sites:
            url = url_template.format(u=username)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    if r.getcode() == 200:
                        body = r.read(1000).decode("utf-8", errors="ignore").lower()
                        if "not found" not in body and "does not exist" not in body:
                            found.append(f"{name}: {url}")
            except Exception:
                pass
        return ScanResult(
            source="WhatsMyName",
            category="web",
            status="found" if found else "none",
            data={"found_profiles": "\n".join(found) if found else "none found", "count": str(len(found))},
        )

    def social_check(self, username):
        links = [
            ("Google", f"https://google.com/search?q={urllib.parse.quote(username)}"),
            ("Twitter", f"https://twitter.com/search?q={urllib.parse.quote(username)}"),
            ("Reddit", f"https://reddit.com/search?q={urllib.parse.quote(username)}"),
        ]
        return ScanResult(
            source="Social Search",
            category="social",
            status="found",
            data={"search_links": "\n".join(f"{n}: {u}" for n, u in links)},
        )
