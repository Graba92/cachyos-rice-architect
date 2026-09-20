# -*- coding: utf-8 -*-
"""
modules/theme_engine.py — Aktive Dotfile- & Theme-Deployment Engine
Verwandelt CachyRice-Architect in ein aktives Werkzeug zum 1-Klick-Anwenden
von kuratierten Starship-, Fastfetch-, Alacritty- und Kitty-Ricing-Konfigurationen.
"""

from __future__ import annotations
import difflib
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

GHOSTTY_CYBER_NEON = r'''# Ghostty — CachyRice-Architect Preset: Cyber-Neon
theme = dark:tokyonight
background = 0d1117
foreground = c9d1d9
cursor-color = 58a6ff
selection-background = 1f6feb
selection-foreground = ffffff
font-family = MesloLGSDZ Nerd Font Mono
font-size = 12
background-opacity = 0.88
background-blur-radius = 20
window-padding-x = 12
window-padding-y = 12
'''

GHOSTTY_CATPPUCCIN = r'''# Ghostty — CachyRice-Architect Preset: Catppuccin Mocha
theme = dark:catppuccin-mocha
background = 1e1e2e
foreground = cdd6f4
cursor-color = f5e0dc
selection-background = 585b70
selection-foreground = cdd6f4
font-family = MesloLGSDZ Nerd Font Mono
font-size = 12
background-opacity = 0.90
background-blur-radius = 20
window-padding-x = 12
window-padding-y = 12
'''

KONSOLE_CYBER_NEON = r'''[General]
Description=CachyRice Cyber Neon
Opacity=0.88
Blur=true

[Background]
Color=13,17,23

[Foreground]
Color=201,209,217

[Color0]
Color=13,17,23

[Color1]
Color=255,123,114

[Color2]
Color=63,185,80

[Color3]
Color=210,153,34

[Color4]
Color=88,166,255

[Color5]
Color=188,140,255

[Color6]
Color=57,197,207

[Color7]
Color=240,246,252
'''

ROFI_WAYLAND_NEON = r'''/* CachyRice-Architect — Rofi Wayland Preset */
configuration {
    modi: "drun,run,window";
    font: "MesloLGSDZ Nerd Font Mono 11";
    show-icons: true;
    display-drun: "🚀 Apps";
    display-run: "💻 Run";
    display-window: "🪟 Windows";
    drun-display-format: "{name}";
}

@theme "/dev/null"

* {
    bg: #0d1117ee;
    fg: #c9d1d9;
    accent: #58a6ff;
    urgent: #ff7b72;
    background-color: transparent;
    text-color: @fg;
}

window {
    width: 600px;
    border: 2px solid @accent;
    border-radius: 12px;
    background-color: @bg;
    padding: 16px;
}

inputbar {
    children: [prompt, entry];
    margin: 0 0 12px 0;
}

prompt {
    text-color: @accent;
    margin: 0 8px 0 0;
}

listview {
    lines: 8;
    columns: 1;
}

element selected {
    background-color: #1f6feb44;
    border-radius: 6px;
    text-color: @accent;
}
'''

WAYBAR_GLASS = r'''/* CachyRice-Architect — Waybar Glassmorphic Preset */
* {
    border: none;
    border-radius: 0;
    font-family: "MesloLGSDZ Nerd Font Mono", monospace;
    font-size: 13px;
    min-height: 0;
}

window#waybar {
    background: rgba(13, 17, 23, 0.75);
    color: #c9d1d9;
    border-bottom: 2px solid rgba(88, 166, 255, 0.4);
}

#workspaces button {
    padding: 0 8px;
    color: #8b949e;
    border-radius: 6px;
    margin: 2px;
}

#workspaces button.active {
    color: #58a6ff;
    background: rgba(88, 166, 255, 0.2);
}

#clock, #battery, #cpu, #memory, #network, #pulseaudio {
    padding: 0 10px;
    margin: 2px 4px;
    border-radius: 6px;
    background: rgba(33, 38, 45, 0.6);
    color: #58a6ff;
}
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
        PresetDefinition(
            category="ghostty",
            name="cyber-neon",
            display_title="Ghostty: Tokyo Night & Neon Blur",
            target_path=Path.home() / ".config" / "ghostty" / "config",
            description="88% Opacity mit KWin-Blur-Radius 20 und Tokyo-Night Akzenten.",
            content=GHOSTTY_CYBER_NEON.strip() + "\n"
        ),
        PresetDefinition(
            category="ghostty",
            name="catppuccin-mocha",
            display_title="Ghostty: Catppuccin Mocha Pastel",
            target_path=Path.home() / ".config" / "ghostty" / "config",
            description="Warmes Catppuccin-Pastell mit KWin-Blur und abgerundetem Padding.",
            content=GHOSTTY_CATPPUCCIN.strip() + "\n"
        ),
        PresetDefinition(
            category="konsole",
            name="cyber-neon",
            display_title="KDE Konsole: Cyber-Neon ColorScheme",
            target_path=Path.home() / ".local" / "share" / "konsole" / "CyberNeon.colorscheme",
            description="Natives KDE Plasma 6 Konsole Farbschema mit 88% Transparenz und Blur.",
            content=KONSOLE_CYBER_NEON.strip() + "\n"
        ),
        PresetDefinition(
            category="rofi",
            name="wayland-neon",
            display_title="Rofi-Wayland: Modern Dark Neon Box",
            target_path=Path.home() / ".config" / "rofi" / "config.rasi",
            description="Abgerundeter Wayland Application Launcher mit Icons und Akzent-Glow.",
            content=ROFI_WAYLAND_NEON.strip() + "\n"
        ),
        PresetDefinition(
            category="waybar",
            name="glass-blur",
            display_title="Waybar: Glassmorphic Floating Top Bar",
            target_path=Path.home() / ".config" / "waybar" / "style.css",
            description="Glassmorphic CSS-Styling für Waybar mit abgerundeten Modulen.",
            content=WAYBAR_GLASS.strip() + "\n"
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
    def get_diff(cls, category: str, name: str) -> Tuple[bool, str]:
        """Erzeugt ein Unified-Diff zwischen aktuellem Dotfile und Preset."""
        preset = cls.find_preset(category, name)
        if not preset:
            return False, f"Preset '{category}/{name}' nicht gefunden."

        target = preset.target_path
        old_lines = []
        if target.exists():
            try:
                old_lines = target.read_text(encoding="utf-8").splitlines(keepends=True)
            except Exception:
                old_lines = []

        new_lines = preset.content.splitlines(keepends=True)
        diff = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=str(target) if target.exists() else "/dev/null",
            tofile=f"preset:{category}/{name}",
            lineterm=""
        ))
        diff_text = "".join(diff)
        return True, diff_text or "✔ Keine Unterschiede (Dateiinhalte sind bereits identisch)."

    @classmethod
    def apply_preset(cls, category: str, name: str, dry_run: bool = False) -> Tuple[bool, str]:
        """Wendet ein Preset sicher an, inklusive automatischem Vorab-Backup."""
        preset = cls.find_preset(category, name)
        if not preset:
            return False, f"Preset '{category}/{name}' nicht gefunden."

        target = preset.target_path
        if dry_run:
            ok, diff_text = cls.get_diff(category, name)
            return True, f"🔍 Dry-Run für '{preset.display_title}' (Ziel: {target}):\n\n{diff_text}"

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

