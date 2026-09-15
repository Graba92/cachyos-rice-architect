# -*- coding: utf-8 -*-
"""
modules/theme_engine.py — Aktive Dotfile- & Theme-Deployment Engine
Verwandelt CachyRice-Architect in ein aktives Werkzeug zum 1-Klick-Anwenden
von kuratierten Starship-, Fastfetch-, Alacritty- und Kitty-Ricing-Konfigurationen.
"""

from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from modules.backup_manager import BackupManager


@dataclass
class PresetDefinition:
    category: str
    name: str
    display_title: str
    target_path: Path
    description: str
    content: str


STARSHIP_CYBER_NEON = r'''# CachyRice-Architect — Preset: Cyber-Neon
# High-contrast neon prompt tailored for CachyOS & KDE Wayland

format = """
[╭─](bold cyan)
[╰─❯](bold magenta) """

continuation_prompt = "[❯❯](bold cyan) "

[os]
disabled = false
style = "bold cyan"

[os.symbols]
Arch = "󰣇 "
CachyOS = "󰣇 "
Linux = "🐧 "

[username]
style_user = "bold yellow"
style_root = "bold red"
format = "[]() "
disabled = false
show_always = false

[directory]
style = "bold cyan"
format = "[]()[]() "
truncation_length = 3
truncation_symbol = "…/"
read_only = " 󰌾"

[git_branch]
symbol = " "
style = "bold purple"
format = "on []() "

[git_status]
style = "bold red"
format = "([\[\]]() )"

[cmd_duration]
min_time = 1000
style = "bold yellow"
format = "took []() "

[character]
success_symbol = "[❯](bold green)"
error_symbol = "[❯](bold red)"
'''

STARSHIP_CATPPUCCIN = r'''# CachyRice-Architect — Preset: Catppuccin Mocha
# Warm pastel theme with modern glyphs

format = """
[╭](surface1) 
[╰─](surface1)[󰅂](pink) """

palette = "catppuccin_mocha"

[directory]
style = "bold lavender"
format = "[]() "
truncation_length = 4

[git_branch]
style = "bold mauve"
symbol = " "
format = "[]() "

[git_status]
style = "bold red"
format = "[]() "

[cmd_duration]
min_time = 2000
style = "bold yellow"
format = "[󱦟 ]() "

[palettes.catppuccin_mocha]
surface1 = "#45475a"
lavender = "#b4befe"
mauve = "#cba6f7"
pink = "#f5c2e7"
yellow = "#f9e2af"
red = "#f38ba8"
'''

FASTFETCH_CLEAN_CACHY = r'''// CachyRice-Architect — Fastfetch Clean CachyOS Preset
{
  "": "https://github.com/fastfetch-cli/fastfetch/raw/dev/doc/json_schema.json",
  "logo": {
    "type": "auto",
    "padding": {
      "top": 1,
      "left": 2,
      "right": 3
    }
  },
  "modules": [
    "title",
    "separator",
    {
      "type": "os",
      "key": "OS         ",
      "keyColor": "cyan"
    },
    {
      "type": "host",
      "key": "Host       ",
      "keyColor": "cyan"
    },
    {
      "type": "kernel",
      "key": "Kernel     ",
      "keyColor": "cyan"
    },
    {
      "type": "uptime",
      "key": "Uptime     ",
      "keyColor": "cyan"
    },
    {
      "type": "packages",
      "key": "Packages   ",
      "keyColor": "cyan"
    },
    {
      "type": "shell",
      "key": "Shell      ",
      "keyColor": "cyan"
    },
    {
      "type": "display",
      "key": "Resolution ",
      "keyColor": "cyan"
    },
    {
      "type": "de",
      "key": "DE         ",
      "keyColor": "cyan"
    },
    {
      "type": "wm",
      "key": "WM         ",
      "keyColor": "cyan"
    },
    {
      "type": "terminal",
      "key": "Terminal   ",
      "keyColor": "cyan"
    },
    {
      "type": "cpu",
      "key": "CPU        ",
      "keyColor": "cyan"
    },
    {
      "type": "gpu",
      "key": "GPU        ",
      "keyColor": "cyan"
    },
    {
      "type": "memory",
      "key": "Memory     ",
      "keyColor": "cyan"
    },
    "break",
    "colors"
  ]
}
'''

ALACRITTY_BLUR_PRESET = r'''# CachyRice-Architect — Alacritty Blur & Modern Typography Preset
# Optimiert für KDE Plasma 6 Wayland & CachyOS

[window]
opacity = 0.88
blur = true
decorations = "Full"

[window.padding]
x = 12
y = 12

[font]
size = 11.5

[font.normal]
family = "JetBrains Mono Nerd Font"
style = "Regular"

[font.bold]
family = "JetBrains Mono Nerd Font"
style = "Bold"

[colors.primary]
background = "#1a1b26"
foreground = "#c0caf5"

[colors.normal]
black = "#15161e"
red = "#f7768e"
green = "#9ece6a"
yellow = "#e0af68"
blue = "#7aa2f7"
magenta = "#bb9af7"
cyan = "#7dcfff"
white = "#a9b1d6"
'''

KITTY_BLUR_PRESET = r'''# CachyRice-Architect — Kitty Modern Wayland Preset
font_family      JetBrains Mono Nerd Font
font_size        11.5
bold_font        auto
italic_font      auto
bold_italic_font auto

window_padding_width 12
background_opacity 0.88
background_blur 1
confirm_os_window_close 0

foreground #c0caf5
background #1a1b26
selection_foreground #none
selection_background #283457

color0 #15161e
color1 #f7768e
color2 #9ece6a
color3 #e0af68
color4 #7aa2f7
color5 #bb9af7
color6 #7dcfff
color7 #a9b1d6
'''


class ThemeEngine:
    """Katalog und Applier für vorkonfigurierte Ricing-Profile."""

    PRESETS: List[PresetDefinition] = [
        PresetDefinition(
            category="starship",
            name="cyber-neon",
            display_title="Starship Prompt: Cyber-Neon",
            target_path=Path.home() / ".config" / "starship.toml",
            description="Cyberpunk/Neon Cyan-Magenta Prompt mit CachyOS-Icon, Git-Status & Timing.",
            content=STARSHIP_CYBER_NEON.strip() + "\n"
        ),
        PresetDefinition(
            category="starship",
            name="catppuccin-mocha",
            display_title="Starship Prompt: Catppuccin Mocha",
            target_path=Path.home() / ".config" / "starship.toml",
            description="Warme Pastell-Ästhetik mit Catppuccin-Farbpalette und Verzeichnis-Glyphen.",
            content=STARSHIP_CATPPUCCIN.strip() + "\n"
        ),
        PresetDefinition(
            category="fastfetch",
            name="clean-cachy",
            display_title="Fastfetch: Clean CachyOS Showcase",
            target_path=Path.home() / ".config" / "fastfetch" / "config.jsonc",
            description="Aufgeräumtes Systeminfo-Display mit Kernel-, BORE-, CPU- und RAM-Balken.",
            content=FASTFETCH_CLEAN_CACHY.strip() + "\n"
        ),
        PresetDefinition(
            category="alacritty",
            name="tokyo-blur",
            display_title="Alacritty: Tokyo Night & Blur",
            target_path=Path.home() / ".config" / "alacritty" / "alacritty.toml",
            description="88% Transparenz mit KWin-Blur, JetBrains Mono Font und Tokyo-Night Theme.",
            content=ALACRITTY_BLUR_PRESET.strip() + "\n"
        ),
        PresetDefinition(
            category="kitty",
            name="tokyo-blur",
            display_title="Kitty: Tokyo Night & Blur",
            target_path=Path.home() / ".config" / "kitty" / "kitty.conf",
            description="88% Opacity mit KWin-Blur-Effekt und 12px Padding für KDE Plasma 6.",
            content=KITTY_BLUR_PRESET.strip() + "\n"
        ),
    ]

    @classmethod
    def get_presets(cls) -> List[PresetDefinition]:
        return cls.PRESETS

    @classmethod
    def find_preset(cls, category: str, name: str) -> Optional[PresetDefinition]:
        cat_lower = category.lower().strip()
        name_lower = name.lower().strip()
        for p in cls.PRESETS:
            if p.category == cat_lower and p.name == name_lower:
                return p
        return None

    @classmethod
    def apply_preset(cls, category: str, name: str) -> Tuple[bool, str]:
        """Wendet ein Preset sicher an, inklusive automatischem Vorab-Backup."""
        preset = cls.find_preset(category, name)
        if not preset:
            return False, f"Preset '{category}/{name}' nicht gefunden."

        target = preset.target_path
        target.parent.mkdir(parents=True, exist_ok=True)

        ok, backup_id = BackupManager.backup_file(target, tag=f"preset_{category}_{name}")
        if not ok:
            return False, f"Konnte Sicherheitsbackup nicht anlegen: {backup_id}"

        try:
            target.write_text(preset.content, encoding="utf-8")
            msg = f"✔ Preset '{preset.display_title}' erfolgreich auf {target} angewendet!"
            if backup_id:
                msg += f"\n  (Vorherige Version gesichert als: {backup_id})"
            return True, msg
        except Exception as e:
            return False, f"Fehler beim Schreiben von {target}: {e}"
