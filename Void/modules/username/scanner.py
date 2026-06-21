"""Username Intelligence — scanner module."""
import json
import urllib.parse
import urllib.request
import urllib.error

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Void.core.engine import ScanResult


_SITES = [
    ("GitHub", "https://github.com/{u}"),
    ("Twitter/X", "https://x.com/{u}"),
    ("Instagram", "https://instagram.com/{u}"),
    ("Reddit", "https://reddit.com/user/{u}"),
    ("Twitch", "https://twitch.tv/{u}"),
    ("YouTube", "https://youtube.com/@{u}"),
    ("Telegram", "https://t.me/{u}"),
    ("Medium", "https://medium.com/@{u}"),
    ("Pinterest", "https://pinterest.com/{u}"),
    ("Snapchat", "https://snapchat.com/add/{u}"),
    ("Steam", "https://steamcommunity.com/id/{u}"),
    ("TikTok", "https://tiktok.com/@{u}"),
    ("Facebook", "https://facebook.com/{u}"),
    ("Dev.to", "https://dev.to/{u}"),
    ("Keybase", "https://keybase.io/{u}"),
    ("Replit", "https://replit.com/@{u}"),
    ("GitLab", "https://gitlab.com/{u}"),
    ("Bitbucket", "https://bitbucket.org/{u}/"),
    ("HackerRank", "https://hackerrank.com/{u}"),
    ("LeetCode", "https://leetcode.com/{u}"),
]


class UsernameScanner:
    def sherlock_scan(self, username):
        found = []
        for name, url_template in _Sites if hasattr(self, '_Sites') else _SITES:
            url = url_template.format(u=username)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    if r.getcode() == 200:
                        found.append({"site": name, "url": url})
            except urllib.error.HTTPError as e:
                if e.code != 404:
                    pass
            except Exception:
                pass
        return ScanResult(
            source="Sherlock",
            category="platforms",
            status="found" if found else "none",
            data={
                "platforms_found": len(found),
                "sites": ", ".join(f["site"] for f in found) if found else "none",
            },
        )

    def maigret_scan(self, username):
        found = []
        check_sites = _SITES[:10]
        for name, url_template in check_sites:
            url = url_template.format(u=username)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    if r.getcode() == 200:
                        found.append({"site": name, "url": url})
            except Exception:
                pass
        return ScanResult(
            source="Maigret",
            category="platforms",
            status="found" if found else "none",
            data={
                "platforms_found": len(found),
                "sites": ", ".join(f["site"] for f in found) if found else "none",
            },
        )

    def whatsmyname_scan(self, username):
        found = []
        for name, url_template in _SITES:
            url = url_template.format(u=username)
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                with urllib.request.urlopen(req, timeout=5) as r:
                    if r.getcode() == 200:
                        found.append({"site": name, "url": url})
            except Exception:
                pass
        return ScanResult(
            source="WhatsMyName",
            category="web",
            status="found" if found else "none",
            data={
                "platforms_found": len(found),
                "sites": ", ".join(f["site"] for f in found) if found else "none",
            },
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
            data={"search_links": " | ".join(f"{n}: {u}" for n, u in links)},
        )
