# ⚡ CachyRice-Architect

[![Platform](https://img.shields.io/badge/Platform-Arch%20Linux%20%7C%20CachyOS-1793d1.svg?style=flat&logo=archlinux)](https://cachyos.org)
[![Desktop](https://img.shields.io/badge/Desktop-KDE%20Plasma%206%20%7C%20Wayland-3399ff.svg)](https://kde.org)
[![TUI](https://img.shields.io/badge/UI-Textual%20%2B%20Rich-green.svg)](https://textual.textualize.io)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](LICENSE)

[🇬🇧 Switch to English Documentation](README.md)

<p align="center">
  <img src="preview_tui.png" alt="CachyRice-Architect TUI" width="900">
</p>

**CachyRice-Architect** ist ein interaktives Terminal-Handbuch und Ricing-Architektur-Tool für **CachyOS / Arch Linux**. Es führt Administratoren und Linux-Enthusiasten strukturiert durch die professionelle Konfiguration von **KDE Plasma 6 (Wayland)**, Standalone-Tiling-Compositoren (**Hyprland**, **Niri**), modernen Terminal-Stacks (**Fish**, **Starship**, **Alacritty**) sowie Kernel- und BORE-Scheduler-Optimierungen.

---

## ✨ Features

- 🖥️ **System- & Ricing-Auditor**: Automatische Erkennung deiner Systemumgebung (Wayland-Compositor, GPU-Treiber, installierte Ricing-Tools, Nerd Fonts, Shell).
- 📖 **Kuratierte Architektur-Guides**:
  1. **KDE Plasma 6 (Wayland) KWin & Effekte**: Transparenz, Klassy-Dekorationen, Blur und KWin-Fensterregeln (z. B. für Glava).
  2. **Standalone Tiling Stacks (Hyprland & Niri)**: Autarke Wayland-Setups, Waybar-Integration, Multimonitor-Setups und Gaps.
  3. **Terminal-Workflow (Fish & Alacritty)**: Starship-Prompt, GPU-beschleunigtes Alacritty-Rendering, Nerd-Font-Typografie.
  4. **System-Tuning & BORE-Scheduler**: Kernel-Optimierungen (x86_64-v3/v4), Sysctl-Tweaks und interaktive Latenzreduktion.
- 🎨 **Duale Oberfläche**:
  - **Textual TUI**: Vollgrafische Terminal-Oberfläche mit Kategorien, Suchleiste und Scroll-Viewer.
  - **CLI-Core**: Direkte Terminal-Befehle für Skripte, schnelle Abfragen und Markdown-Export.
- 💾 **Export-Funktion**: Exportiere alle Anleitungen mit einem Befehl in eigenständige Markdown-Dateien für dein lokales Wiki.

---

## 🏛️ Projektstruktur

```text
cachyos-rice-architect/
├── main.py                     # Zentraler Einstiegspunkt (CLI & TUI)
├── run.sh                      # Universal-Startskript
├── setup.sh                    # Indestructible Installations-Skript (pacman / venv)
├── requirements.txt            # Python-Abhängigkeiten
├── README.md                   # Englische Dokumentation
├── README_DE.md                # Deutsche Dokumentation (dieses Dokument)
├── .gitignore                  # Git-Ausschlussregeln
│
├── data/
│   └── guides.json             # Strukturierte Wissensdatenbank der Ricing-Guides
│
└── modules/
    ├── __init__.py             # Modul-Initialisierung
    ├── network.py              # Update-Prüfung gegen CachyOS Wiki
    ├── storage.py              # JSON-Parser, Suchindex & Markdown-Exporter
    ├── system_info.py          # Hardware-, Desktop- & Tool-Auditing
    └── tui.py                  # Textual-basierte Vollbild-TUI
```

---

## 🚀 Installation

### 1. Schnelleinrichtung (Empfohlen)

Das Skript `setup.sh` erkennt CachyOS / Arch Linux und installiert Abhängigkeiten via `pacman` oder richtet ein lokales `.venv` ein:

```bash
git clone https://github.com/Graba92/cachyos-rice-architect.git
cd cachyos-rice-architect
chmod +x setup.sh run.sh
./setup.sh
```

### 2. Nativ via Pacman (Arch Linux / CachyOS)

```bash
sudo pacman -S --needed python-rich python-textual
```

### 3. Via pip / Virtualenv

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 🖥️ Verwendung

### 1. Interaktive TUI starten
```bash
./run.sh
# oder
python3 main.py
```

### 2. CLI-Befehle (Headless)

```bash
# System- & Ricing-Tools Diagnose ausführen:
python3 main.py --info

# Alle verfügbaren Guides tabellarisch auflisten:
python3 main.py --list

# Bestimmte Anleitung direkt im Terminal lesen (z. B. Guide ID 1):
python3 main.py --read 1

# Gezielte Volltext- und Tag-Suche (z. B. nach 'kwin'):
python3 main.py --search kwin

# Alle Guides als Markdown-Dateien exportieren:
python3 main.py --export ./guides_backup/

# Klassisches Konsolenmenü (Fallback ohne Textual):
python3 main.py --cli
```

---

## 📄 Lizenz

Dieses Projekt ist lizenziert unter der [MIT-Lizenz](LICENSE).
