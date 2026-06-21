# VOID OSINT TOOLKIT

**Real OSINT framework · Wraps actual tools · Standalone · No paid APIs**

```
╔══════════════════════════════════════════════════════════════╗
║██╗   ██╗ ██████╗ ██╗██████╗     ██████╗ ███████╗██╗███╗   ██╗████████╗║
║██║   ██║██╔═══██╗██║██╔══██╗   ██╔═══██╗██╔════╝██║████╗  ██║╚══██╔══╝║
║██║   ██║██║   ██║██║██║  ██║   ██║   ██║███████╗██║██╔██╗ ██║   ██║   ║
║╚██╗ ██╔╝██║   ██║██║██║  ██║   ██║   ██║╚════██║██║██║╚██╗██║   ██║   ║
║ ╚████╔╝ ╚██████╔╝██║██████╔╝   ╚██████╔╝███████║██║██║ ╚████║   ██║   ║
║  ╚═══╝   ╚═════╝ ╚═╝╚═════╝     ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝   ╚═╝   ║
╚══════════════════════════════════════════════════════════════╝
```

---

## What This Is

VOID OSINT is a **wrapper framework** — it does NOT reimplement OSINT tools. It orchestrates real, proven tools and presents results in a unified terminal interface.

**No paid APIs. No commercial SaaS. No mock data. Pure local execution.**

---

## Quick Install

### Linux / macOS

```bash
git clone https://github.com/9uz3/Void-OSINT-Toolkit.git
cd Void-OSINT-Toolkit
bash install.sh
voidosint
```

### Windows

```batch
git clone https://github.com/9uz3/Void-OSINT-Toolkit.git
cd Void-OSINT-Toolkit
install.bat
voidosint
```

### Run directly

```bash
./voidosint
```

---

## Requirements

- Python 3.8+ (3.10+ recommended)
- Terminal: 100x30 minimum
- OS: Linux, macOS, Windows 10/11, Kali, Ubuntu, Debian, WSL

---

## Integrated Tools

| Tool | Function | Category |
|------|----------|----------|
| **Holehe** | Email enumeration — finds services linked to email | Email |
| **Sherlock** | Username enumeration across 400+ platforms | Username |
| **Maigret** | Username enumeration — 2500+ sites, advanced filtering | Username |
| **PhoneInfoga** | Phone number investigation | Phone |
| **theHarvester** | Email, host, subdomain harvesting from public sources | Domain |
| **Sublist3r** | Subdomain enumeration | Domain |
| **ExifTool** | Metadata extraction from files | Image |
| **h8mail** | Breach correlation without paid APIs | Breach |
| **SpiderFoot** | Automated OSINT (optional) | Framework |
| **Recon-ng** | Reconnaissance framework (optional) | Framework |

---

## Usage

```bash
voidosint              # Launch dashboard
voidosint doctor       # System diagnostics
voidosint update       # Install/update dependencies
voidosint modules      # List available modules
```

### Controls

| Key | Action |
|-----|--------|
| `↑ ↓` | Navigate categories |
| `← →` | Navigate tools |
| `Enter` | Select / Launch |
| `F` | Fuzzy search |
| `Q` | Quit |

---

## How It Works

```
User Input → VOID Engine → Real OSINT Tools → JSON Results → Terminal UI
                                    │
                     ┌──────────────┼──────────────┐
                     │              │              │
                   holehe        sherlock      theHarvester
                   maigret       phoneinfoga   sublist3r
                   h8mail        exiftool      ...
```

Each module is a **wrapper** that:
1. Calls the real tool via subprocess
2. Parses the output
3. Returns structured JSON
4. The UI displays results

---

## Project Structure

```
Void-OSINT-Toolkit/
├── voidosint              # Launcher
├── install.sh / .bat      # Installers
├── Void/
│   ├── main.py            # Entry point
│   ├── requirements.txt   # All dependencies
│   ├── core/
│   │   └── engine.py      # OSINT orchestration engine
│   ├── modules/
│   │   ├── report.py      # Report generation (TXT)
│   │   ├── email/scanner.py   # → holehe wrapper
│   │   ├── username/scanner.py # → sherlock/maigret wrapper
│   │   ├── phone/scanner.py   # → phoneinfoga wrapper
│   │   ├── ip/scanner.py      # → ip-api + proxycheck
│   │   └── domain/scanner.py  # → theHarvester + sublist3r
│   ├── lib/               # UI, config, constants
│   └── data/reports/      # Generated reports
```

---

## Reports

Every scan generates a TXT report with:
- Target
- Date and time
- All findings from each tool

Reports saved to `Void/data/reports/`.

---

## Philosophy

> "Don't reinvent the wheel — orchestrate the best wheels."

VOID OSINT uses mature, community-proven tools:
- **Holehe** for email enumeration (not a custom implementation)
- **Sherlock/Maigret** for username lookup (not HTTP probes)
- **theHarvester** for domain recon (not a custom scraper)
- **PhoneInfoga** for phone analysis (not a regex parser)

The framework is the **glue** — the tools do the real work.

---

## Disclaimer

For educational and authorized security testing purposes only. Users are responsible for proper authorization. See [DISCLAIMER.md](DISCLAIMER.md).

---

## Credits

- **Author**: [9uz3](https://github.com/9uz3)
- **Community**: [Void](https://discord.gg/esXFX6gkq)
- **Tools**: [Holehe](https://github.com/megadose/holehe), [Sherlock](https://github.com/sherlock-project/sherlock), [Maigret](https://github.com/soxoj/maigret), [theHarvester](https://github.com/laramies/theHarvester), [PhoneInfoga](https://github.com/sundowndev/PhoneInfoga)

---

## License

See [Void/LICENSE](Void/LICENSE).
