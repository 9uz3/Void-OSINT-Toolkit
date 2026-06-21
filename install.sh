#!/usr/bin/env bash
# Void OSINT Toolkit - Installer
# Usage: bash install.sh [--system]

set -e

DIR="$(cd "$(dirname "$0")" && pwd)"
SCRIPT="$DIR/voidosint"
BIN="$HOME/.local/bin"

if [ "$1" = "--system" ] && [ "$(id -u)" = "0" ]; then
    BIN="/usr/local/bin"
elif [ "$1" = "--system" ]; then
    echo "[!] --system requires root. Try: sudo bash install.sh --system"
    echo "    Installing to ~/.local/bin instead."
fi

mkdir -p "$BIN"
chmod +x "$SCRIPT"
ln -sf "$SCRIPT" "$BIN/voidosint"
echo "[+] Installed: $BIN/voidosint -> $SCRIPT"

# Fix PATH
if [[ ":$PATH:" != *":$BIN:"* ]]; then
    SHELL_CONFIG=""
    case "$SHELL" in
        *zsh) SHELL_CONFIG="$HOME/.zshrc" ;;
        *bash) SHELL_CONFIG="$HOME/.bashrc" ;;
    esac
    if [ -n "$SHELL_CONFIG" ]; then
        echo "" >> "$SHELL_CONFIG"
        echo "# Void OSINT Toolkit" >> "$SHELL_CONFIG"
        echo "export PATH=\"\$PATH:$BIN\"" >> "$SHELL_CONFIG"
        echo "[+] Added $BIN to PATH in $SHELL_CONFIG"
        echo "    Run: source $SHELL_CONFIG"
    fi
fi

echo ""
echo "  ┌─────────────────────────────────┐"
echo "  │  Void OSINT Toolkit installed!  │"
echo "  │                                 │"
echo "  │  Just type: voidosint           │"
echo "  └─────────────────────────────────┘"
echo ""
echo "  First run auto-installs Python dependencies."
echo "  OSINT tools (holehe, sherlock, maigret, etc.) are installed via pip."
