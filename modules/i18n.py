#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
modules/i18n.py — Internationalization (i18n) Engine for CachyOS Rice-Architect.
Provides comprehensive German (de_DE) and English (en_US) translations with dynamic runtime switching.
"""

from __future__ import annotations
import json
from pathlib import Path
from typing import Dict, Any

CONFIG_FILE = Path.home() / ".config" / "cachyos-rice-architect" / "config.json"

_STRINGS: Dict[str, Dict[str, str]] = {
    "de": {
        # General & Navigation
        "app_title": "CACHYOS RICE-ARCHITECT",
        "app_subtitle": "Advanced Ricing & System Customization Suite │ KDE Plasma 6 / Wayland",
        "btn_quit": "Beenden",
        "btn_cancel": "Abbrechen",
        "btn_confirm": "Bestätigen",
        "btn_close": "Schließen",
        "btn_refresh": "Aktualisieren",
        "btn_apply": "Anwenden",
        "btn_backup": "Backup erstellen",
        "btn_rollback": "Rollback",
        "btn_lang_toggle": "🌐 Sprache: DE (Taste: L)",
        "status_ready": "Bereit",
        "status_success": "Erfolgreich ausgeführt.",
        "status_error": "Fehlgeschlagen.",

        # CLI Menu
        "menu_title": "Aktion wählen",
        "menu_opt_1": "Alle Module & Anleitungen durchstöbern",
        "menu_opt_2": "Nach Kategorien filtern",
        "menu_opt_3": "Nach Schlagwörtern (Tags) filtern",
        "menu_opt_4": "Volltextsuche (Titel, Tags, Inhalt)",
        "menu_opt_5": "System-Diagnose & Ricing-Tools Check",
        "menu_opt_6": "Anleitungen exportieren (Markdown)",
        "menu_opt_7": "🎨 Ricing-Presets & Dotfiles anwenden (1-Klick)",
        "menu_opt_8": "🔄 Dotfile-Backups & 1-Klick Rollback",
        "menu_opt_lang": "Sprache wechseln (Deutsch / English)",
        "menu_opt_quit": "Beenden",

        # TUI Tabs
        "tab_guides": "1. 📖 Ricing-Guides",
        "tab_presets": "2. 🎨 Theme Presets & Dotfiles",
        "tab_doctor": "3. 🩺 Rice-Doctor",
        "tab_backups": "4. 🔄 Backup & Rollback",

        # Presets & Themes
        "presets_title": "🎨 Ricing-Presets & Dotfiles (1-Klick Installer)",
        "presets_desc": "Wähle ein kuratiertes CachyOS Rice-Theme für KDE Plasma 6 Wayland.",
        "btn_apply_preset": "Ausgewähltes Preset installieren",

        # Rice Doctor
        "doctor_title": "🩺 CachyOS Rice-Doctor & System-Check",
        "doctor_score": "Ricing-Kompatibilitäts-Score",
        "col_check": "Komponente / Check",
        "col_status": "Status",
        "col_details": "Details & Installation",

        # Backups
        "backup_title": "🔄 Dotfile-Sicherungen & Wiederherstellung",
        "col_backup_id": "Backup-ID",
        "col_backup_date": "Erstellungsdatum",
        "col_backup_files": "Gesicherte Dateien",

        # CLI
        "cli_lang_saved": "[OK] Sprache dauerhaft auf '{lang}' gesetzt.",
    },
    "en": {
        # General & Navigation
        "app_title": "CACHYOS RICE-ARCHITECT",
        "app_subtitle": "Advanced Ricing & System Customization Suite │ KDE Plasma 6 / Wayland",
        "btn_quit": "Quit",
        "btn_cancel": "Cancel",
        "btn_confirm": "Confirm",
        "btn_close": "Close",
        "btn_refresh": "Refresh",
        "btn_apply": "Apply",
        "btn_backup": "Create Backup",
        "btn_rollback": "Rollback",
        "btn_lang_toggle": "🌐 Language: EN (Key: L)",
        "status_ready": "Ready",
        "status_success": "Successfully executed.",
        "status_error": "Failed.",

        # CLI Menu
        "menu_title": "Select Action",
        "menu_opt_1": "Browse all modules & guides",
        "menu_opt_2": "Filter by category",
        "menu_opt_3": "Filter by tags",
        "menu_opt_4": "Fulltext search (Title, tags, content)",
        "menu_opt_5": "System diagnostics & ricing tools check",
        "menu_opt_6": "Export guides (Markdown)",
        "menu_opt_7": "🎨 Apply ricing presets & dotfiles (1-Click)",
        "menu_opt_8": "🔄 Dotfile backups & 1-click rollback",
        "menu_opt_lang": "Toggle Language (German / English)",
        "menu_opt_quit": "Quit",

        # TUI Tabs
        "tab_guides": "1. 📖 Ricing Guides",
        "tab_presets": "2. 🎨 Theme Presets & Dotfiles",
        "tab_doctor": "3. 🩺 Rice-Doctor",
        "tab_backups": "4. 🔄 Backup & Rollback",

        # Presets & Themes
        "presets_title": "🎨 Ricing Presets & Dotfiles (1-Click Installer)",
        "presets_desc": "Select a curated CachyOS rice theme for KDE Plasma 6 Wayland.",
        "btn_apply_preset": "Install Selected Preset",

        # Rice Doctor
        "doctor_title": "🩺 CachyOS Rice-Doctor & System Check",
        "doctor_score": "Ricing Compatibility Score",
        "col_check": "Component / Check",
        "col_status": "Status",
        "col_details": "Details & Installation",

        # Backups
        "backup_title": "🔄 Dotfile Backups & Restoration",
        "col_backup_id": "Backup ID",
        "col_backup_date": "Creation Date",
        "col_backup_files": "Archived Files",

        # CLI
        "cli_lang_saved": "[OK] Language permanently set to '{lang}'.",
    },
}

_current_lang = "de"


def load_configured_language() -> str:
    """Lädt die gespeicherte Sprache aus der Konfiguration."""
    global _current_lang
    try:
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                lang = data.get("language", "de")
                if lang in ("de", "en"):
                    _current_lang = lang
                    return lang
    except Exception:
        pass
    return _current_lang


def save_configured_language(lang: str) -> None:
    """Speichert die gewählte Sprache persistent."""
    try:
        CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
        data = {}
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        data["language"] = lang
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass


def set_language(lang: str) -> None:
    """Setzt die aktive Sprache ('de' oder 'en')."""
    global _current_lang
    if lang.lower().startswith("en"):
        _current_lang = "en"
    else:
        _current_lang = "de"


def get_language() -> str:
    """Gibt den aktuellen Sprachcode ('de' oder 'en') zurück."""
    return _current_lang


def toggle_language() -> str:
    """Wechselt zwischen Deutsch und Englisch und speichert die Wahl."""
    global _current_lang
    _current_lang = "en" if _current_lang == "de" else "de"
    save_configured_language(_current_lang)
    return _current_lang


def t(key: str, **kwargs: Any) -> str:
    """Übersetzt einen Schlüssel in die aktive Sprache mit optionaler Formatierung."""
    lang_dict = _STRINGS.get(_current_lang, _STRINGS["en"])
    text = lang_dict.get(key)
    if text is None:
        text = _STRINGS["en"].get(key, key)
    if kwargs:
        try:
            return text.format(**kwargs)
        except Exception:
            return text
    return text
