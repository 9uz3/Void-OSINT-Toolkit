"""Domain Intelligence — wrapper for theHarvester + amass + whatweb."""
import os
import re
import socket
import ssl
import subprocess
import tempfile

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
            if os.name == "nt":
                with tempfile.NamedTemporaryFile(mode="w", suffix=".xml", delete=False) as tmp:
                    tmp_path = tmp.name
                try:
                    proc = subprocess.run(
                        ["theHarvester", "-d", domain, "-b", "bing,yahoo,duckduckgo", "-f", tmp_path],
                        capture_output=True, text=True, timeout=120
                    )
                    if os.path.exists(tmp_path):
                        with open(tmp_path, "r", errors="ignore") as f:
                            output = f.read()
                    else:
                        output = proc.stdout
                finally:
                    if os.path.exists(tmp_path):
                        os.unlink(tmp_path)
            else:
                proc = subprocess.run(
                    ["theHarvester", "-d", domain, "-b", "bing,yahoo,duckduckgo", "-f", "/dev/stdout"],
                    capture_output=True, text=True, timeout=120
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

    def detect_tech(self, domain):
        try:
            proc = subprocess.run(
                ["whatweb", "--color=never", "-a", "3", f"https://{domain}"],
                capture_output=True, text=True, timeout=30
            )
            output = proc.stdout
            technologies = []
            for match in re.finditer(r'\[([^\]]+)\]', output):
                tech = match.group(1)
                if tech and tech not in ("200 OK", "301 Moved"):
                    technologies.append(tech)
            if not technologies:
                for line in output.split(","):
                    line = line.strip()
                    if line and not line.startswith("http") and not line.startswith("["):
                        technologies.append(line.split(":")[0].strip())
            return ScanResult(
                source="WhatWeb",
                category="technology",
                status="found" if technologies else "none",
                data={"technologies": technologies[:15], "count": len(technologies)},
            )
        except FileNotFoundError:
            return ScanResult(source="WhatWeb", category="technology", status="error", error="whatweb not installed")
        except Exception as e:
            return ScanResult(source="WhatWeb", category="technology", status="error", error=str(e))

    def amass_enum(self, domain):
        try:
            proc = subprocess.run(
                ["amass", "enum", "-passive", "-d", domain, "-timeout", "5"],
                capture_output=True, text=True, timeout=60
            )
            output = proc.stdout
            subdomains = []
            for line in output.split("\n"):
                line = line.strip()
                if line and "." in line and not line.startswith("["):
                    subdomains.append(line)
            return ScanResult(
                source="Amass",
                category="subdomains",
                status="found" if subdomains else "none",
                data={"subdomains": subdomains[:50], "count": len(subdomains)},
            )
        except FileNotFoundError:
            return ScanResult(source="Amass", category="subdomains", status="error", error="amass not installed: apt install amass")
        except Exception as e:
            return ScanResult(source="Amass", category="subdomains", status="error", error=str(e))
