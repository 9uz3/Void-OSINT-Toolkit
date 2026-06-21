"""Domain Intelligence — wrapper for theHarvester + sublist3r."""
import json
import re
import socket
import ssl
import subprocess
import urllib.request

from core.engine import ScanResult


class DomainScanner:
    def whois_lookup(self, domain):
        try:
            import whois
            w = whois.whois(domain)
            return ScanResult(
                source="WHOIS",
                category="registration",
                status="found",
                data={
                    "domain": domain,
                    "registrar": str(w.registrar or "?"),
                    "created": str(w.creation_date or "?"),
                    "expires": str(w.expiration_date or "?"),
                    "name_servers": w.name_servers or [],
                    "org": str(w.org or w.name or "?"),
                    "country": str(w.country or "?"),
                },
            )
        except ImportError:
            return ScanResult(source="WHOIS", category="registration", status="error", error="python-whois not installed")
        except Exception as e:
            return ScanResult(source="WHOIS", category="registration", status="error", error=str(e))

    def dns_records(self, domain):
        try:
            import dns.resolver
            records = {}
            for qtype in ("A", "AAAA", "MX", "NS", "TXT", "CNAME"):
                try:
                    answers = dns.resolver.resolve(domain, qtype, lifetime=5)
                    records[qtype] = [str(r) for r in answers]
                except Exception:
                    pass
            return ScanResult(
                source="DNS",
                category="dns",
                status="found" if records else "none",
                data={"records": records},
            )
        except ImportError:
            return ScanResult(source="DNS", category="dns", status="error", error="dnspython not installed")
        except Exception as e:
            return ScanResult(source="DNS", category="dns", status="error", error=str(e))

    def ssl_check(self, domain):
        try:
            ctx = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=8) as sock:
                with ctx.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
            if cert:
                subject = dict(x for x in cert.get("subject", []) for x in [x]) if cert.get("subject") else {}
                issuer = dict(x for x in cert.get("issuer", []) for x in [x]) if cert.get("issuer") else {}
                san = cert.get("subjectAltName", [])
                return ScanResult(
                    source="SSL",
                    category="certificate",
                    status="found",
                    data={
                        "subject_cn": str(subject.get("commonName", "?")),
                        "issuer_cn": str(issuer.get("commonName", "?")),
                        "valid_from": str(cert.get("notBefore", "?")),
                        "valid_until": str(cert.get("notAfter", "?")),
                        "san_count": len(san),
                    },
                )
        except Exception as e:
            return ScanResult(source="SSL", category="certificate", status="error", error=str(e))

    def theharvester_scan(self, domain):
        try:
            proc = subprocess.run(
                ["theHarvester", "-d", domain, "-b", "all", "-f", "/dev/stdout"],
                capture_output=True, text=True, timeout=60
            )
            output = proc.stdout
            emails = []
            hosts = []
            for line in output.split("\n"):
                line = line.strip()
                if "@" in line and "." in line:
                    emails.append(line)
                elif line and not line.startswith("[") and not line.startswith("-") and not line.startswith("*"):
                    if "." in line and len(line) < 100:
                        hosts.append(line)
            return ScanResult(
                source="theHarvester",
                category="harvesting",
                status="found" if emails or hosts else "none",
                data={"emails": emails[:20], "hosts": hosts[:20], "email_count": len(emails), "host_count": len(hosts)},
            )
        except FileNotFoundError:
            return ScanResult(source="theHarvester", category="harvesting", status="error", error="theHarvester not installed")
        except Exception as e:
            return ScanResult(source="theHarvester", category="harvesting", status="error", error=str(e))

    def sublist3r_scan(self, domain):
        try:
            proc = subprocess.run(
                ["sublist3r", "-d", domain],
                capture_output=True, text=True, timeout=60
            )
            output = proc.stdout
            subdomains = []
            for line in output.split("\n"):
                line = line.strip()
                if line and "." in line and not line.startswith("[") and not line.startswith("Sub"):
                    subdomains.append(line)
            return ScanResult(
                source="Sublist3r",
                category="subdomains",
                status="found" if subdomains else "none",
                data={"subdomains": subdomains[:50], "count": len(subdomains)},
            )
        except FileNotFoundError:
            return ScanResult(source="Sublist3r", category="subdomains", status="error", error="sublist3r not installed")
        except Exception as e:
            return ScanResult(source="Sublist3r", category="subdomains", status="error", error=str(e))

    def enumerate_subdomains(self, domain):
        common = ["www", "mail", "ftp", "admin", "api", "dev", "staging", "test", "blog", "shop"]
        found = []
        for sub in common:
            fqdn = f"{sub}.{domain}"
            try:
                socket.getaddrinfo(fqdn, None)
                found.append(fqdn)
            except Exception:
                pass
        return ScanResult(
            source="DNS Brute",
            category="subdomains",
            status="found" if found else "none",
            data={"subdomains": found, "count": len(found)},
        )

    def detect_tech(self, domain):
        url = f"https://{domain}"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                headers_str = str(r.headers)
                body = r.read(1024).decode("utf-8", errors="ignore").lower()
            combined = headers_str.lower() + body
            detected = []
            patterns = [
                ("WordPress", r"/wp-content/|/wp-admin/"),
                ("nginx", r"nginx"),
                ("Apache", r"Apache"),
                ("Cloudflare", r"cloudflare"),
                ("PHP", r"PHP|Zend"),
                ("Python", r"Python|Django|Flask"),
                ("Node.js", r"Node\.?[Jj]s|Express"),
                ("Java", r"Java|Tomcat"),
                ("React", r"react|__NEXT_DATA__"),
            ]
            for name, pattern in patterns:
                if re.search(pattern, combined, re.I):
                    detected.append(name)
            return ScanResult(
                source="Tech Detect",
                category="technology",
                status="found" if detected else "none",
                data={"technologies": detected, "count": len(detected)},
            )
        except Exception as e:
            return ScanResult(source="Tech Detect", category="technology", status="error", error=str(e))
