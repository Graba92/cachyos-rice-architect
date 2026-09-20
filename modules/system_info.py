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


def check_nerd_fonts() -> List[str]:
    """Prüft, welche Nerd Fonts oder Coding-Fonts im System installiert sind."""
    if not shutil.which("fc-list"):
        return []
    try:
        import subprocess
        res = subprocess.run(["fc-list", ":", "family"], capture_output=True, text=True, timeout=3)
        families = set()
        for line in res.stdout.splitlines():
            for part in line.split(","):
                p = part.strip()
                p_lower = p.lower()
                if any(k in p_lower for k in ["nerd", "fira", "jetbrains", "meslo", "cascadia", "hack"]):
                    families.add(p)
        return sorted(list(families))
    except Exception:
        return []


def run_rice_doctor() -> dict:
    """Führt eine umfassende Ricing- & Wayland-Systemdiagnose durch."""
    sys_data = get_full_system_data()
    fonts = check_nerd_fonts()
    tools = sys_data.get("tools", {})

    checks = []

    # 1. Wayland & Compositor
    session = sys_data.get("session_type", "").lower()
    desktop = sys_data.get("desktop", "")
    if session == "wayland":
        checks.append({"name": "Wayland Sitzung", "status": "OK", "msg": f"Aktive Wayland-Session ({desktop})"})
    else:
        checks.append({"name": "Wayland Sitzung", "status": "WARN", "msg": f"Aktive Sitzung: {session} (X11). Einige Ricing-Effekte erfordern Wayland"})

    # 2. Nerd Fonts
    if fonts:
        checks.append({"name": "Nerd Fonts & Glyphen", "status": "OK", "msg": f"{len(fonts)} Fonts gefunden ({', '.join(fonts[:2])}{'...' if len(fonts) > 2 else ''})"})
    else:
        checks.append({"name": "Nerd Fonts & Glyphen", "status": "WARN", "msg": "Keine Nerd Fonts gefunden. Icons in Starship/Waybar werden möglicherweise nicht dargestellt"})

    # 3. Terminals
    term_tools = tools.get("Terminals", [])
    installed_terms = [t["label"] for t in term_tools if t["installed"]]
    if installed_terms:
        checks.append({"name": "Moderne GPU-Terminals", "status": "OK", "msg": f"{len(installed_terms)} installiert ({', '.join(installed_terms)})"})
    else:
        checks.append({"name": "Moderne GPU-Terminals", "status": "WARN", "msg": "Kein modernes Terminal wie Alacritty, Kitty oder Ghostty gefunden"})

    # 4. Shell & Prompt
    shell_tools = tools.get("Shell & Prompt", [])
    installed_shells = [t["label"] for t in shell_tools if t["installed"]]
    checks.append({"name": "Shell-Ökosystem", "status": "OK" if "Starship Prompt" in [t["label"] for t in shell_tools if t["installed"]] or "Fish Shell" in installed_shells else "INFO", "msg": f"Bereit: {', '.join(installed_shells)}"})

    # 5. Launcher & Visuals
    launchers = [t["label"] for t in tools.get("Launcher", []) if t["installed"]]
    if launchers:
        checks.append({"name": "App-Launcher (Wayland)", "status": "OK", "msg": f"Aktiv: {', '.join(launchers)}"})
    else:
        checks.append({"name": "App-Launcher (Wayland)", "status": "INFO", "msg": "Kein Wayland-Launcher wie Rofi-Wayland oder Fuzzel installiert"})

    ok_count = sum(1 for c in checks if c["status"] == "OK")
    score = int((ok_count / len(checks)) * 100) if checks else 0

    return {
        "score": score,
        "checks": checks,
        "fonts": fonts,
        "system": sys_data
    }


def display_rice_doctor(report: dict) -> None:
    score = report.get("score", 0)
    score_color = "bold green" if score >= 80 else "bold yellow" if score >= 60 else "bold red"

    table = Table(title=f"🎨 CachyRice-Architect Doctor (Rice-Score: [{score_color}]{score}%[/{score_color}])", border_style="bright_magenta", show_header=True)
    table.add_column("Komponente / Subsystem", style="bold cyan", width=30)
    table.add_column("Status", justify="center", width=10)
    table.add_column("Details & Empfehlungen", style="white")

    for check in report.get("checks", []):
        st = check.get("status", "INFO")
        if st == "OK":
            st_str = "[bold green]✔ OK[/]"
        elif st == "WARN":
            st_str = "[bold yellow]⚠ WARN[/]"
        elif st == "FAIL":
            st_str = "[bold red]✘ FEHLER[/]"
        else:
            st_str = "[dim]ℹ INFO[/]"
        table.add_row(check.get("name", ""), st_str, check.get("msg", ""))

    console.print(table)

