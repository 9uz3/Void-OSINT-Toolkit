"""Phone Intelligence — wrapper for PhoneInfoga."""
import json
import subprocess

from core.engine import ScanResult


class PhoneScanner:
    def validate_number(self, phone):
        try:
            import phonenumbers
            from phonenumbers import carrier, geocoder, timezone, PhoneNumberType

            pn = phonenumbers.parse(phone, None)
            is_valid = phonenumbers.is_valid_number(pn)
            is_possible = phonenumbers.is_possible_number(pn)
            fmt_intl = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
            fmt_e164 = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.E164)
            fmt_national = phonenumbers.format_number(pn, phonenumbers.PhoneNumberFormat.NATIONAL)

            type_map = {
                PhoneNumberType.MOBILE: "Mobile",
                PhoneNumberType.FIXED_LINE: "Landline",
                PhoneNumberType.VOIP: "VoIP",
                PhoneNumberType.TOLL_FREE: "Toll-Free",
                PhoneNumberType.UNKNOWN: "Unknown",
            }
            num_type = type_map.get(phonenumbers.number_type(pn), "Unknown")

            return ScanResult(
                source="Phonenumbers",
                category="validation",
                status="found",
                data={
                    "valid": is_valid,
                    "possible": is_possible,
                    "international": fmt_intl,
                    "e164": fmt_e164,
                    "national": fmt_national,
                    "type": num_type,
                    "country_code": f"+{pn.country_code}",
                },
            )
        except Exception as e:
            return ScanResult(source="Phonenumbers", category="validation", status="error", error=str(e))

    def identify_carrier(self, phone):
        try:
            proc = subprocess.run(
                ["phoneinfoga", "scan", "-n", phone, "-o", "json"],
                capture_output=True, text=True, timeout=20
            )
            output = proc.stdout
            try:
                data = json.loads(output)
                return ScanResult(
                    source="PhoneInfoga",
                    category="carrier",
                    status="found",
                    data={"raw_output": data},
                )
            except json.JSONDecodeError:
                lines = [l.strip() for l in output.split("\n") if l.strip()]
                return ScanResult(
                    source="PhoneInfoga",
                    category="carrier",
                    status="found" if lines else "none",
                    data={"output": lines},
                )
        except FileNotFoundError:
            return ScanResult(source="PhoneInfoga", category="carrier", status="error", error="phoneinfoga not installed: pip install phoneinfoga")
        except Exception as e:
            return ScanResult(source="PhoneInfoga", category="carrier", status="error", error=str(e))

    def geolocate(self, phone):
        try:
            import phonenumbers
            from phonenumbers import geocoder, timezone
            pn = phonenumbers.parse(phone, None)
            country = geocoder.description_for_number(pn, "en") or "Unknown"
            tz_list = timezone.time_zones_for_number(pn) or []
            return ScanResult(
                source="Geocoder",
                category="location",
                status="found" if country != "Unknown" else "none",
                data={"country": country, "timezone": ", ".join(tz_list)},
            )
        except Exception as e:
            return ScanResult(source="Geocoder", category="location", status="error", error=str(e))

    def assess_risk(self, phone):
        try:
            import phonenumbers
            pn = phonenumbers.parse(phone, None)
            is_valid = phonenumbers.is_valid_number(pn)
            risk = 0
            if not is_valid:
                risk += 50
            national = str(pn.national_number)
            if any(national.startswith(p) for p in ["555", "000", "123"]):
                risk += 30
            level = "HIGH" if risk >= 70 else ("MEDIUM" if risk >= 40 else "LOW")
            return ScanResult(
                source="Risk Assessment",
                category="risk",
                status="found",
                data={"risk_score": risk, "risk_level": level},
            )
        except Exception as e:
            return ScanResult(source="Risk Assessment", category="risk", status="error", error=str(e))
