#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import platform
import shutil
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

console = Console()

def get_os_release():
    info = {}
    if os.path.exists("/etc/os-release"):
        try:
            with open("/etc/os-release", "r", encoding="utf-8") as f:
                for line in f:
                    if "=" in line:
                        k, v = line.strip().split("=", 1)
                        info[k] = v.strip('"\'')
        except Exception:
            pass
    return info

def get_cpu_info():
    if os.path.exists("/proc/cpuinfo"):
        try:
            with open("/proc/cpuinfo", "r", encoding="utf-8") as f:
                for line in f:
                    if "model name" in line:
                        return line.split(":", 1)[1].strip()
        except Exception:
            pass
    return platform.processor() or "Unbekannt"

def check_installed_tools():
    categories = {
        "Compositor & DE": [
            ("kwin_wayland", "KWin Wayland (Plasma)"),
            ("hyprland", "Hyprland"),
            ("niri", "Niri"),
            ("sway", "Sway"),
        ],
        "Terminals": [
            ("alacritty", "Alacritty"),
            ("kitty", "Kitty"),
            ("ghostty", "Ghostty"),
            ("foot", "Foot"),
            ("konsole", "KDE Konsole"),
        ],
        "Shell & Prompt": [
            ("fish", "Fish Shell"),
            ("starship", "Starship Prompt"),
            ("zsh", "Zsh Shell"),
            ("bash", "Bash Shell"),
        ],
        "Bars & Widgets": [
            ("waybar", "Waybar"),
            ("ags", "Aylur's GTK Shell (AGS)"),
            ("eww", "Eww Widgets"),
        ],
        "Launcher": [
            ("rofi", "Rofi / Rofi-Wayland"),
            ("wofi", "Wofi"),
            ("fuzzel", "Fuzzel"),
            ("walker", "Walker"),
        ],
        "Wallpaper & Eye-Candy": [
            ("swww", "swww Wallpaper-Daemon"),
            ("hyprpaper", "Hyprpaper"),
            ("mpvpaper", "mpvpaper"),
            ("swaybg", "swaybg"),
            ("cava", "Cava Audio Visualizer"),
        ],
        "TUI & Monitoring": [
            ("fastfetch", "Fastfetch"),
            ("btop", "btop Monitoring"),
            ("yazi", "Yazi File Manager"),
            ("lazygit", "LazyGit"),
            ("nvim", "Neovim"),
        ],
        "Theming & Tools": [
            ("kvantummanager", "Kvantum Manager"),
            ("qt6ct", "Qt6ct Settings"),
            ("qt5ct", "Qt5ct Settings"),
            ("yay", "yay AUR Helper"),
            ("pacman", "Pacman Package Manager"),
        ],
    }

    results = {}
    for cat, tool_list in categories.items():
        results[cat] = []
        for bin_name, label in tool_list:
            path = shutil.which(bin_name)
            installed = path is not None
            results[cat].append({
                "binary": bin_name,
                "label": label,
                "installed": installed,
                "path": path or ""
            })
    return results

def get_full_system_data():
    os_info = get_os_release()
    return {
        "distro": os_info.get("PRETTY_NAME", "Linux"),
        "kernel": platform.release(),
        "desktop": os.environ.get("XDG_CURRENT_DESKTOP", "Unbekannt"),
        "session_type": os.environ.get("XDG_SESSION_TYPE", "wayland"),
        "shell": os.environ.get("SHELL", "Unbekannt"),
        "terminal": os.environ.get("TERM", "Unbekannt"),
        "cpu": get_cpu_info(),
        "tools": check_installed_tools()
    }

def display_system_overview():
    os_info = get_os_release()
    distro_name = os_info.get("PRETTY_NAME", "Linux")
    kernel = platform.release()
    desktop = os.environ.get("XDG_CURRENT_DESKTOP", "Unbekannt")
    session_type = os.environ.get("XDG_SESSION_TYPE", "Unbekannt")
    shell = os.environ.get("SHELL", "Unbekannt")
    terminal = os.environ.get("TERM", "Unbekannt")
    cpu = get_cpu_info()

    table = Table(title="Aktuelle Systemumgebung", show_header=True, header_style="bold cyan")
    table.add_column("Eigenschaft", style="yellow")
    table.add_column("Wert", style="white")

    table.add_row("Distribution", distro_name)
    table.add_row("Kernel", kernel)
    table.add_row("Desktop-Umgebung", desktop)
    table.add_row("Display-Server / Sitzung", f"[bold green]{session_type}[/bold green]" if session_type == "wayland" else session_type)
    table.add_row("Aktive Shell", shell)
    table.add_row("Terminal-Emulator ($TERM)", terminal)
    table.add_row("Prozessor", cpu)

    console.print(table)
    console.print()

    tools_data = check_installed_tools()
    tool_table = Table(title="Status installierter Ricing-Tools & Komponenten", show_header=True, header_style="bold magenta")
    tool_table.add_column("Kategorie", style="cyan", width=22)
    tool_table.add_column("Komponente", style="white", width=28)
    tool_table.add_column("Status", width=14)
    tool_table.add_column("Pfad", style="dim")

    for cat, tools in tools_data.items():
        for t in tools:
            status = "[bold green]✔ Installiert[/bold green]" if t["installed"] else "[dim red]✖ Fehlt[/dim red]"
            path_str = t["path"] if t["installed"] else "-"
            tool_table.add_row(cat, t["label"], status, path_str)

    console.print(tool_table)
