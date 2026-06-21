"""IP Intelligence — scanner module."""
import json
import socket
import urllib.request

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from Void.core.engine import ScanResult


class IPScanner:
    def geolocate(self, ip):
        try:
            url = f"http://ip-api.com/json/{ip}?fields=66842623"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                data = json.loads(r.read().decode())
            if data.get("status") == "success":
                return ScanResult(
                    source="ip-api",
                    category="geolocation",
                    status="found",
                    data={
                        "ip": data.get("query", ip),
                        "country": data.get("country", "?"),
                        "region": data.get("regionName", "?"),
                        "city": data.get("city", "?"),
                        "zip": data.get("zip", "?"),
                        "lat": data.get("lat", "?"),
                        "lon": data.get("lon", "?"),
                        "isp": data.get("isp", "?"),
                        "org": data.get("org", "?"),
                        "as": data.get("as", "?"),
                        "timezone": data.get("timezone", "?"),
                    },
                    url=url,
                )
            return ScanResult(source="ip-api", category="geolocation", status="error", error=data.get("message", "Query failed"))
        except Exception as e:
            return ScanResult(source="ip-api", category="geolocation", status="error", error=str(e))

    def detect_vpn(self, ip):
        try:
            url = f"https://proxycheck.io/v2/{ip}?vpn=1&asn=1"
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=10) as r:
                data = json.loads(r.read().decode())
            if data.get("status") == "ok":
                res = data.get(ip, {})
                return ScanResult(
                    source="ProxyCheck",
                    category="vpn_detection",
                    status="found",
                    data={
                        "proxy": res.get("proxy", "no"),
                        "type": res.get("type", "N/A"),
                        "provider": res.get("provider", "N/A"),
                        "asn": res.get("asn", "N/A"),
                        "country": res.get("country", "N/A"),
                    },
                    url=url,
                )
            return ScanResult(source="ProxyCheck", category="vpn_detection", status="error", error=data.get("message", "Query failed"))
        except Exception as e:
            return ScanResult(source="ProxyCheck", category="vpn_detection", status="error", error=str(e))

    def whois_lookup(self, ip):
        try:
            from ipwhois import IPWhois
            obj = IPWhois(ip)
            res = obj.lookup_rdap(depth=1)
            network = res.get("network", {})
            return ScanResult(
                source="WHOIS",
                category="registration",
                status="found",
                data={
                    "asn": f"AS{res.get('asn', '?')}",
                    "asn_cidr": res.get("asn_cidr", "?"),
                    "asn_country": res.get("asn_country_code", "?"),
                    "asn_registry": res.get("asn_registry", "?"),
                    "cidr": network.get("cidr", "?"),
                    "name": network.get("name", "?"),
                    "org": network.get("org", "?"),
                },
            )
        except ImportError:
            return ScanResult(source="WHOIS", category="registration", status="error", error="ipwhois not installed")
        except Exception as e:
            return ScanResult(source="WHOIS", category="registration", status="error", error=str(e))

    def common_ports(self, ip):
        common = [21, 22, 25, 53, 80, 443, 8080, 8443]
        open_ports = []
        for port in common:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(1)
                result = s.connect_ex((ip, port))
                if result == 0:
                    open_ports.append(port)
                s.close()
            except Exception:
                pass
        return ScanResult(
            source="Port Scan",
            category="ports",
            status="found" if open_ports else "none",
            data={
                "open_ports": ", ".join(str(p) for p in open_ports) if open_ports else "none found",
                "ports_scanned": ", ".join(str(p) for p in common),
            },
        )
