"""Domain Intelligence — scanner module."""
import json
import re
import socket
import ssl
import urllib.request

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Void.core.engine import ScanResult


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
                    "updated": str(w.updated_date or "?"),
                    "name_servers": ", ".join(w.name_servers or ["?"]),
                    "org": str(w.org or w.name or "?"),
                    "country": str(w.country or "?"),
                    "emails": ", ".join(w.emails or ["?"]),
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
            for qtype in ("A", "AAAA", "MX", "NS", "TXT", "CNAME", "SOA"):
                try:
                    answers = dns.resolver.resolve(domain, qtype, lifetime=5)
                    records[qtype] = [str(r) for r in answers]
                except Exception:
                    pass
            return ScanResult(
                source="DNS",
                category="dns",
                status="found" if records else "none",
                data={"records": json.dumps(records, indent=2) if records else "no records"},
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
                subject = dict(cert.get("subject", []))
                issuer = dict(cert.get("issuer", []))
                san = cert.get("subjectAltName", [])
                return ScanResult(
                    source="SSL",
                    category="certificate",
                    status="found",
                    data={
                        "subject_cn": str(subject.get("commonName", "?")),
                        "issuer_cn": str(issuer.get("commonName", "?")),
                        "issuer_org": str(issuer.get("organizationName", "?")),
                        "valid_from": str(cert.get("notBefore", "?")),
                        "valid_until": str(cert.get("notAfter", "?")),
                        "san_count": str(len(san)),
                        "serial": str(cert.get("serialNumber", "?")),
                    },
                )
        except Exception as e:
            return ScanResult(source="SSL", category="certificate", status="error", error=str(e))

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
            source="Subdomain Enum",
            category="subdomains",
            status="found" if found else "none",
            data={
                "subdomains_found": len(found),
                "subdomains": ", ".join(found) if found else "none found",
            },
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
                data={"technologies": ", ".join(detected) if detected else "none detected"},
            )
        except Exception as e:
            return ScanResult(source="Tech Detect", category="technology", status="error", error=str(e))
