#!/usr/bin/env bash
# ==============================================================================
# CachyRice-Architect — Universal Starter Script
# ==============================================================================
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 1. Python-Prüfung
if ! command -v python3 &> /dev/null; then
    echo -e "\033[1;31m[FEHLER]\033[0m Python 3 wurde nicht im Pfad gefunden." >&2
    exit 1
fi

# 2. Ausführung über lokales .venv (falls vorhanden) oder System-Python
if [ -d "$SCRIPT_DIR/.venv" ] && [ -f "$SCRIPT_DIR/.venv/bin/python3" ]; then
    exec "$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/main.py" "$@"
else
    # Abhängigkeiten im System prüfen
    MISSING_DEPS=()
    if ! python3 -c "import rich" &> /dev/null; then
        MISSING_DEPS+=("python-rich")
    fi
    if ! python3 -c "import textual" &> /dev/null; then
        MISSING_DEPS+=("python-textual")
    fi

    if [ ${#MISSING_DEPS[@]} -gt 0 ]; then
        echo -e "\033[1;33m[HINWEIS]\033[0m Benötigte Python-Bibliotheken fehlen: ${MISSING_DEPS[*]}" >&2
        echo -e "Bitte führe \033[1;36m./setup.sh\033[0m aus oder installiere via: \033[1;36msudo pacman -S ${MISSING_DEPS[*]}\033[0m" >&2
        exit 1
    fi

    exec python3 "$SCRIPT_DIR/main.py" "$@"
fi
