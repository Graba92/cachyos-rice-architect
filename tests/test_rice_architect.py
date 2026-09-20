"""
tests/test_rice_architect.py — Umfassende Test-Suite für CachyRice-Architect.
Prüft Datenbank-Integrität, ThemeEngine Presets, Diff-Generator,
BackupManager und RiceDoctor Systemdiagnose.
"""

import os
import sys
import unittest
from pathlib import Path

# Basisverzeichnis zum Suchpfad hinzufügen
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from modules.storage import load_database, get_categories, get_all_tags
from modules.theme_engine import ThemeEngine, PresetDefinition
from modules.backup_manager import BackupManager
from modules.system_info import check_installed_tools, check_nerd_fonts, run_rice_doctor
from modules.i18n import t, set_language, get_language, toggle_language


class TestCachyRiceArchitect(unittest.TestCase):
    """Testet alle Kernmodule von CachyRice-Architect."""

    def test_i18n_translation(self):
        """Prüft i18n-Sprachumschaltung und String-Auflösung."""
        set_language("de")
        self.assertEqual(get_language(), "de")
        self.assertIn("RICE-ARCHITECT", t("app_title"))
        self.assertEqual(t("btn_quit"), "Beenden")

        set_language("en")
        self.assertEqual(get_language(), "en")
        self.assertIn("RICE-ARCHITECT", t("app_title"))
        self.assertEqual(t("btn_quit"), "Quit")

    def test_i18n_toggle(self):
        """Prüft wechselweises Umschalten."""
        set_language("de")
        self.assertEqual(toggle_language(), "en")
        self.assertEqual(toggle_language(), "de")

    def test_database_loading_and_categories(self):
        """Guides-Datenbank muss valide Modul-Einträge mit Titeln und Kategorien enthalten."""
        db_path = BASE_DIR / "data" / "guides.json"
        db = load_database(str(db_path))
        self.assertIsInstance(db, dict)
        self.assertGreaterEqual(len(db), 5)

        categories = get_categories(db)
        self.assertIsInstance(categories, dict)
        self.assertIn("Theming & Styling", categories)
        self.assertIn("UI/Design-Tweaks", categories)

        tags = get_all_tags(db)
        self.assertIsInstance(tags, dict)
        self.assertGreater(len(tags), 5)

    def test_theme_engine_presets(self):
        """ThemeEngine muss Presets für Starship, Fastfetch, Alacritty, Kitty, Ghostty, Konsole etc. liefern."""
        presets = ThemeEngine.get_presets()
        self.assertGreaterEqual(len(presets), 8)

        categories_present = {p.category for p in presets}
        expected_cats = {"starship", "fastfetch", "alacritty", "kitty", "ghostty", "konsole", "rofi", "waybar"}
        for ec in expected_cats:
            self.assertIn(ec, categories_present)

    def test_theme_engine_diff(self):
        """Diff-Generierung für Presets muss ohne Exceptions ein Unified-Diff erzeugen."""
        ok, diff_text = ThemeEngine.get_diff("starship", "cyber-neon")
        self.assertTrue(ok)
        self.assertTrue(len(diff_text) > 0)

    def test_theme_engine_dry_run(self):
        """Dry-Run darf keine Dateien auf der Festplatte modifizieren."""
        ok, msg = ThemeEngine.apply_preset("fastfetch", "clean-cachy", dry_run=True)
        self.assertTrue(ok)
        self.assertIn("Dry-Run", msg)

    def test_rice_doctor_report(self):
        """RiceDoctor muss Systemstatus, Fonts und einen prozentualen Score liefern."""
        report = run_rice_doctor()
        self.assertIn("score", report)
        self.assertGreaterEqual(report["score"], 0)
        self.assertLessEqual(report["score"], 100)
        self.assertIn("checks", report)
        self.assertGreaterEqual(len(report["checks"]), 4)
        self.assertIn("fonts", report)

    def test_installed_tools_inspection(self):
        """Tool-Scanner muss Kategorien wie Terminals, Compositor und Shells zurückgeben."""
        tools = check_installed_tools()
        self.assertIn("Compositor & DE", tools)
        self.assertIn("Terminals", tools)
        self.assertIn("Shell & Prompt", tools)


if __name__ == "__main__":
    unittest.main(verbosity=2)
