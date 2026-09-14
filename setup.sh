#!/usr/bin/env bash
# ==============================================================================
# CachyRice-Architect — Production Setup & Dependency Installer
# Bulletproof Bash Engineer Architecture (Arch Linux / CachyOS / Generic Linux)
# ==============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_FILE="$SCRIPT_DIR/setup.log"

# Dual logging
exec > >(tee -a "$LOG_FILE") 2>&1

cleanup() {
    local exit_code=$?
    if [ $exit_code -ne 0 ]; then
        echo -e "\n\033[1;31m[!] Setup wurde mit Fehlercode $exit_code abgebrochen.\033[0m"
        echo -e "Details findest du im Log: $LOG_FILE"
    fi
}
trap cleanup EXIT ERR

# Farben
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}====================================================================${NC}"
echo -e "${CYAN}${BOLD}   ⚡ CachyRice-Architect — Setup & Systemvorbereitung              ${NC}"
echo -e "${CYAN}${BOLD}====================================================================${NC}"
echo -e "Startzeit: $(date '+%Y-%m-%d %H:%M:%S')\n"

# 1. Pre-Flight Checks
echo -e "${CYAN}[1/4] Pre-Flight Checks...${NC}"
if ! command -v python3 &>/dev/null; then
    echo -e "${RED}[FEHLER] Python 3 wurde nicht gefunden. Bitte installiere Python 3.${NC}" >&2
    exit 1
fi
PYTHON_VER=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
echo -e "${GREEN}[✓] Python 3 gefunden (Version $PYTHON_VER)${NC}"

# 2. Abhängigkeiten auflösen (Arch Linux / CachyOS nativ vs. venv)
echo -e "\n${CYAN}[2/4] Abhängigkeiten prüfen & installieren...${NC}"

HAS_RICH=false
HAS_TEXTUAL=false

python3 -c "import rich" &>/dev/null && HAS_RICH=true || true
python3 -c "import textual" &>/dev/null && HAS_TEXTUAL=true || true

if [ "$HAS_RICH" = true ] && [ "$HAS_TEXTUAL" = true ]; then
    echo -e "${GREEN}[✓] Alle erforderlichen Bibliotheken (rich, textual) sind bereits vorhanden.${NC}"
else
    echo -e "${YELLOW}[i] Fehlende Module erkannt. Suche nach Installationsoptionen...${NC}"
    
    if command -v pacman &>/dev/null; then
        echo -e "${CYAN}[+] Arch Linux / CachyOS erkannt. Installiere Systempakete via pacman...${NC}"
        PKGS=()
        [ "$HAS_RICH" = false ] && PKGS+=("python-rich")
        [ "$HAS_TEXTUAL" = false ] && PKGS+=("python-textual")
        
        echo -e "Führe aus: sudo pacman -S --needed --noconfirm ${PKGS[*]}"
        if sudo pacman -S --needed --noconfirm "${PKGS[@]}"; then
            echo -e "${GREEN}[✓] Systempakete erfolgreich via pacman installiert.${NC}"
        else
            echo -e "${YELLOW}[!] pacman fehlgeschlagen oder keine Root-Rechte. Richte lokales venv ein...${NC}"
            python3 -m venv "$SCRIPT_DIR/.venv"
            "$SCRIPT_DIR/.venv/bin/pip" install --upgrade pip
            "$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
            echo -e "${GREEN}[✓] Lokales venv unter .venv eingerichtet.${NC}"
        fi
    else
        echo -e "${CYAN}[+] Richte isolierte virtuelle Umgebung (.venv) ein...${NC}"
        python3 -m venv "$SCRIPT_DIR/.venv"
        "$SCRIPT_DIR/.venv/bin/pip" install --upgrade pip
        "$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt"
        echo -e "${GREEN}[✓] Virtuelle Umgebung erfolgreich erstellt & Pakete installiert.${NC}"
    fi
fi

# 3. Berechtigungen setzen
echo -e "\n${CYAN}[3/4] Dateiberechtigungen setzen...${NC}"
chmod +x "$SCRIPT_DIR/main.py"
[ -f "$SCRIPT_DIR/run.sh" ] && chmod +x "$SCRIPT_DIR/run.sh"
[ -f "$SCRIPT_DIR/setup.sh" ] && chmod +x "$SCRIPT_DIR/setup.sh"
echo -e "${GREEN}[✓] Alle Skripte sind nun ausführbar.${NC}"

# 4. Funktions-Test
echo -e "\n${CYAN}[4/4] Funktions-Test (Smoke-Test)...${NC}"
if [ -d "$SCRIPT_DIR/.venv" ]; then
    "$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/main.py" --help >/dev/null
else
    python3 "$SCRIPT_DIR/main.py" --help >/dev/null
fi
echo -e "${GREEN}[✓] CachyRice-Architect CLI-Core reagiert einwandfrei.${NC}"

echo -e "\n${GREEN}${BOLD}====================================================================${NC}"
echo -e "${GREEN}${BOLD}   Setup erfolgreich abgeschlossen! 🚀                              ${NC}"
echo -e "${GREEN}${BOLD}====================================================================${NC}"
echo -e "Starte das Tool mit:"
echo -e "  ${CYAN}./run.sh${NC}  oder  ${CYAN}python3 main.py${NC}\n"