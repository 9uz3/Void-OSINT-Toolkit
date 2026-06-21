# VOID OSINT TOOLKIT

**Terminal OSINT framework · 32 tools · 12 categories · Rich dashboard**

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

## Quick Install

### Linux / macOS

```bash
git clone https://github.com/9uz3/Void-OSINT-Toolkit.git
cd Void-OSINT-Toolkit
bash install.sh
voidosint
```

Or install system-wide (requires root):

```bash
sudo bash install.sh --system
voidosint
```

### Windows

```batch
git clone https://github.com/9uz3/Void-OSINT-Toolkit.git
cd Void-OSINT-Toolkit
install.bat
voidosint
```

### Run directly (no install)

```bash
# Linux/macOS
./voidosint

# Windows
voidosint.bat
```

First run auto-installs Python dependencies. No venv needed.

---

## Requirements

- **Python 3.8+** (Python 3.10+ recommended)
- **Terminal**: 100x30 minimum size
- **OS**: Linux, macOS, Windows 10/11, Kali Linux, Ubuntu, Debian, WSL

---

## What It Does

VOID OSINT is a modular OSINT investigation framework that runs entirely in your terminal. It wraps multiple OSINT tools behind a visual interface — you never need to type raw commands.

| Category | Tools | Description |
|----------|-------|-------------|
| **EMAIL** | Lookup, Validate, Breach Check | Scan 90+ platforms for email presence |
| **PHONE** | Number Info, Carrier ID | Parse, validate, and identify phone numbers |
| **IP / NET** | Geolocation, VPN Detection, WHOIS | Investigate IP addresses and network data |
| **USERNAME** | Cross-Platform Search, Pattern Analysis | Find usernames across 185+ platforms |
| **DOMAIN** | WHOIS, DNS Records, SSL Certificates | Domain investigation and infrastructure |
| **SOCIAL** | Profile Search, Social Scan | Search social media platforms |
| **BREACH** | Breach Check, Breach Search | Check for compromised credentials |
| **WEB** | Tech Detection, Headers, Robots.txt | Website technology fingerprinting |
| **DORK** | Google Dork Generator, Search | Generate and execute Google dorks |
| **IMAGE** | EXIF Viewer, Image Metadata | Extract image metadata and EXIF data |

---

## Controls

| Key | Action |
|-----|--------|
| `↑ ↓` | Navigate categories (sidebar) |
| `← →` | Navigate tools (grid) |
| `Enter` | Select / Launch tool |
| `F` | Fuzzy search across all tools |
| `Q` / `Ctrl+C` | Quit |

---

## Configuration

### First-Run Wizard

On first launch, VOID OSINT presents a setup wizard:

1. **Language**: Choose Français or English
2. **Theme**: Pick from 12 color themes + rainbow
3. **Username**: Set your operator name
4. **Boot Animation**: Enable or skip cinematic boot

### Manual Config

Edit `Void/config/settings.json`:

```json
{
  "language": "en",
  "theme": "white",
  "username": "Operator",
  "skip_boot": false,
  "setup_complete": true
}
```

### Available Themes

| Theme | Color |
|-------|-------|
| red | Rouge / Red |
| green | Vert / Green |
| blue | Bleu / Blue |
| yellow | Jaune / Yellow |
| purple | Violet / Purple |
| cyan | Cyan |
| orange | Orange |
| pink | Rose / Pink |
| lime | Lime |
| white | Blanc / White |
| rose | Rose vif |
| gold | Or / Gold |
| rainbow | Arc-en-ciel |

---

## Commands

```bash
voidosint              # Launch the dashboard
voidosint doctor       # System diagnostics
voidosint update       # Install/update dependencies
voidosint modules      # List available OSINT modules
```

---

## Project Structure

```
Void-OSINT-Toolkit/
├── voidosint              # Linux launcher
├── voidosint.bat          # Windows launcher
├── install.sh             # Linux installer
├── install.bat            # Windows installer
├── Void/
│   ├── main.py            # Entry point
│   ├── requirements.txt   # Python dependencies
│   ├── config/
│   │   └── settings.json  # User configuration
│   ├── data/
│   │   └── reports/       # Scan reports (JSON + TXT)
│   └── lib/
│       ├── entry.py       # Initialization
│       ├── router.py      # Main dashboard
│       ├── ui.py          # Card rendering
│       ├── pages.py       # Page definitions
│       ├── boot.py        # Cinematic boot animation
│       ├── constants.py   # Colors, themes, paths
│       ├── config.py      # Settings management
│       ├── setup.py       # First-run wizard
│       ├── scanner.py     # Email/Username scanner
│       ├── tools_osint.py # 24 OSINT tools
│       ├── phintel.py     # Phone intelligence
│       ├── search.py      # Fuzzy search
│       └── deps.py        # Dependency manager
```

---

## Reports

Every scan generates reports in `Void/data/reports/`:

- **JSON** — structured data for programmatic use
- **TXT** — human-readable format

Example filenames:
```
email_user_at_gmail_com_20260620_212158.json
username_john_20260620_212041.txt
phone_5511999998888_20260620_213419.json
```

---

## Disclaimer

This tool is for **educational and authorized security testing purposes only**.

Users are responsible for ensuring they have proper authorization before running any investigation. The authors are not responsible for misuse of this tool.

See [DISCLAIMER.md](DISCLAIMER.md) for full details.

---

## Credits

- **Author**: [9uz3](https://github.com/9uz3)
- **Community**: [Void](https://discord.gg/esXFX6gkq)
- **Built with**: [Rich](https://github.com/Textualize/rich), [user-scanner](https://github.com/user-scanner/user-scanner)

---

## License

See [Void/LICENSE](Void/LICENSE).
