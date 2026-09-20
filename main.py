#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import argparse
import platform
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text

from modules.network import check_web_updates
from modules.storage import (
    load_database,
    export_to_markdown,
    export_single_guide,
    get_categories,
    get_all_tags,
)
from modules.system_info import display_system_overview, run_rice_doctor, display_rice_doctor
from modules.tui import run_tui
from modules.theme_engine import ThemeEngine
from modules.backup_manager import BackupManager

console = Console()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "data", "guides.json")

class CachyArchitectTUI:
    def __init__(self, db_path: str = DB_FILE, skip_network: bool = False):
        self.db = load_database(db_path)
        if not self.db:
            console.print("[bold red]Abbruch: Guides-Datenbank konnte nicht initialisiert werden.[/bold red]")
            sys.exit(1)
        self.skip_network = skip_network
        self.categories = get_categories(self.db)
        self.tags = get_all_tags(self.db)

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self):
        self.clear_screen()
        session_type = os.environ.get("XDG_SESSION_TYPE", "wayland")
        desktop = os.environ.get("XDG_CURRENT_DESKTOP", "KDE")
        kernel = platform.release()

        meta_line = f"[cyan]Kernel:[/cyan] {kernel}  |  [cyan]Desktop:[/cyan] {desktop} ({session_type})  |  [cyan]Guides:[/cyan] {len(self.db)}"
        header = Panel(
            Text.from_markup(
                "[bold cyan]⚡ CachyRice-Architect CLI-Core[/bold cyan]\n"
                "[white]Advanced Ricing & System Control für CachyOS / KDE Plasma 6 / Wayland[/white]\n"
                f"[dim]{meta_line}[/dim]"
            ),
            border_style="cyan",
            expand=False,
            padding=(0, 2)
        )
        console.print(header)
        console.print()

    def run(self):
        if not self.skip_network:
            check_web_updates(skip=False)
            Prompt.ask("[dim]Drücke Enter, um das Hauptmenü zu öffnen...[/dim]")

        while True:
            self.print_header()
            table = Table(show_header=False, box=None, padding=(0, 2))
            table.add_column("Key", style="bold green", justify="right")
            table.add_column("Action", style="white")

            table.add_row("[1]", "Alle Module & Anleitungen durchstöbern")
            table.add_row("[2]", "Nach Kategorien filtern")
            table.add_row("[3]", "Nach Schlagwörtern (Tags) filtern")
            table.add_row("[4]", "Volltextsuche (Titel, Tags, Inhalt)")
            table.add_row("[5]", "System-Diagnose & Ricing-Tools Check")
            table.add_row("[6]", "Anleitungen exportieren (Markdown)")
            table.add_row("[7]", "🎨 Ricing-Presets & Dotfiles anwenden (1-Klick Installer)")
            table.add_row("[8]", "🔄 Dotfile-Backups & 1-Klick Rollback")
            table.add_row("[q]", "Beenden")

            console.print(table)
            console.print()

            choice = Prompt.ask(
                "[bold blue]>[/bold blue] Aktion wählen",
                choices=["1", "2", "3", "4", "5", "6", "7", "8", "q", "Q"]
            )

            if choice == "1":
                self.menu_browse()
            elif choice == "2":
                self.menu_categories()
            elif choice == "3":
                self.menu_tags()
            elif choice == "4":
                self.menu_search()
            elif choice == "5":
                self.menu_system_info()
            elif choice == "6":
                self.menu_export()
            elif choice == "7":
                self.menu_presets()
            elif choice == "8":
                self.menu_backups()
            elif choice.lower() == "q":
                console.print("\n[bold green]Architect beendet. Viel Erfolg beim Ricing![/bold green]")
                sys.exit(0)

    def menu_browse(self, filter_keys=None, title_prefix="Verfügbare Ricing-Module"):
        while True:
            self.print_header()
            console.print(f"[bold yellow]{title_prefix}:[/bold yellow]\n")

            table = Table(box=None)
            table.add_column("ID", style="cyan", justify="right")
            table.add_column("Kategorie", style="magenta")
            table.add_column("Thema", style="white")
            table.add_column("Tags", style="dim")

            target_keys = filter_keys if filter_keys is not None else list(self.db.keys())
            sorted_keys = sorted(target_keys, key=lambda x: int(x) if x.isdigit() else x)

            for key in sorted_keys:
                data = self.db[key]
                tags_preview = ", ".join(data.get("tags", []))
                table.add_row(f"[{key}]", data.get("category", ""), data.get("title", ""), tags_preview)

            console.print(table)
            console.print()

            choices = sorted_keys + ["b", "B"]
            choice = Prompt.ask("[bold blue]>[/bold blue] Modul-ID eingeben (oder [b] für Zurück)", choices=choices)

            if choice.lower() == 'b':
                break
            self.display_article(choice)

    def menu_categories(self):
        while True:
            self.print_header()
            console.print("[bold yellow]Kategorien-Übersicht:[/bold yellow]\n")

            cat_keys = list(self.categories.keys())
            table = Table(box=None)
            table.add_column("Nr.", style="cyan", justify="right")
            table.add_column("Kategorie", style="white")
            table.add_column("Anzahl Guides", style="green", justify="center")

            for idx, cat in enumerate(cat_keys, start=1):
                count = len(self.categories[cat])
                table.add_row(f"[{idx}]", cat, str(count))

            console.print(table)
            console.print()

            num_choices = [str(i) for i in range(1, len(cat_keys) + 1)] + ["b", "B"]
            choice = Prompt.ask("[bold blue]>[/bold blue] Kategorie-Nummer wählen (oder [b] für Zurück)", choices=num_choices)

            if choice.lower() == 'b':
                break

            selected_cat = cat_keys[int(choice) - 1]
            matching_ids = self.categories[selected_cat]
            self.menu_browse(filter_keys=matching_ids, title_prefix=f"Kategorie: {selected_cat}")

    def menu_tags(self):
        while True:
            self.print_header()
            console.print("[bold yellow]Verfügbare Schlagwörter (Tags):[/bold yellow]\n")

            tag_list = sorted(self.tags.keys())
            # Format in columns
            cols = 4
            tag_table = Table(box=None, show_header=False)
            for _ in range(cols):
                tag_table.add_column(style="cyan")

            for i in range(0, len(tag_list), cols):
                row_items = tag_list[i:i+cols]
                while len(row_items) < cols:
                    row_items.append("")
                tag_table.add_row(*[f"#{t}" if t else "" for t in row_items])

            console.print(tag_table)
            console.print()

            query = Prompt.ask("[bold blue]>[/bold blue] Tag eingeben (ohne #, oder [b] für Zurück)").strip().lower()
            if query == 'b' or not query:
                break

            matching_ids = self.tags.get(query, [])
            if not matching_ids:
                # Partial match search
                matching_ids = []
                for t, ids in self.tags.items():
                    if query in t:
                        matching_ids.extend([i for i in ids if i not in matching_ids])

            if not matching_ids:
                console.print(f"\n[red]Keine Guides mit dem Schlagwort '{query}' gefunden.[/red]")
                Prompt.ask("\n[dim]Enter drücken...[/dim]")
                continue

            self.menu_browse(filter_keys=matching_ids, title_prefix=f"Tag: #{query}")

    def menu_search(self):
        self.print_header()
        query = Prompt.ask("[bold yellow]Suchbegriff eingeben (Titel, Inhalt oder Tags)[/bold yellow]").strip().lower()

        if not query:
            return

        results = []
        for key, data in self.db.items():
            content = data.get("content", "").lower()
            title = data.get("title", "").lower()
            tags = " ".join(data.get("tags", [])).lower()
            category = data.get("category", "").lower()

            if query in tags or query in title or query in content or query in category:
                results.append(key)

        if not results:
            console.print(f"\n[red]Keine Treffer für '{query}' gefunden.[/red]")
            Prompt.ask("\n[dim]Enter drücken...[/dim]")
            return

        self.menu_browse(filter_keys=results, title_prefix=f"{len(results)} Suchtreffer für '{query}'")

    def menu_system_info(self):
        self.print_header()
        display_system_overview()
        console.print()
        Prompt.ask("[bold blue]>[/bold blue] Drücke Enter, um zum Hauptmenü zurückzukehren...")

    def menu_export(self):
        self.print_header()
        console.print("[bold yellow]Export-Optionen:[/bold yellow]\n")
        console.print("  [cyan][1][/cyan] Gesamtdokumentation aller Guides exportieren (Markdown)")
        console.print("  [cyan][2][/cyan] Einzelne Anleitung gezielt exportieren")
        console.print("  [dim][b] Zurück zum Hauptmenü[/dim]\n")

        choice = Prompt.ask("[bold blue]>[/bold blue] Auswahl", choices=["1", "2", "b", "B"])
        if choice == "1":
            export_to_markdown(self.db)
            Prompt.ask("\n[dim]Enter drücken...[/dim]")
        elif choice == "2":
            guide_id = Prompt.ask("[bold blue]>[/bold blue] Modul-ID eingeben", choices=list(self.db.keys()) + ["b", "B"])
            if guide_id.lower() != 'b':
                export_single_guide(guide_id, self.db)
                Prompt.ask("\n[dim]Enter drücken...[/dim]")

    def menu_presets(self):
        self.print_header()
        console.print("[bold yellow]🎨 Kuratierte Ricing-Presets (1-Klick Installer):[/bold yellow]\n")
        presets = ThemeEngine.get_presets()
        table = Table(header_style="bold cyan", border_style="cyan")
        table.add_column("Nr.", justify="right", style="bold green")
        table.add_column("Kategorie", style="magenta")
        table.add_column("Preset Name", style="bold white")
        table.add_column("Zielpfad", style="dim")
        table.add_column("Beschreibung", style="white")

        for idx, p in enumerate(presets, 1):
            table.add_row(str(idx), p.category, p.name, str(p.target_path), p.description)

        console.print(table)
        console.print("\n[dim]Wähle eine Nummer zum Anwenden, oder [b] für Zurück.[/dim]")
        valid_choices = [str(i) for i in range(1, len(presets) + 1)] + ["b", "B"]
        choice = Prompt.ask("[bold blue]>[/bold blue] Auswahl", choices=valid_choices)
        if choice.lower() != "b":
            chosen = presets[int(choice) - 1]
            confirm = Prompt.ask(f"Preset '{chosen.display_title}' jetzt auf {chosen.target_path} anwenden? [y/N]", default="n")
            if confirm.lower() == "y":
                ok, msg = ThemeEngine.apply_preset(chosen.category, chosen.name)
                if ok:
                    console.print(f"\n[bold green]{msg}[/bold green]")
                else:
                    console.print(f"\n[bold red]{msg}[/bold red]")
            Prompt.ask("\n[dim]Enter drücken...[/dim]")

    def menu_backups(self):
        self.print_header()
        console.print("[bold yellow]🔄 Dotfile-Backups & Rollback-Manager:[/bold yellow]\n")
        backups = BackupManager.list_backups()
        if not backups:
            console.print("[dim]Keine Backups vorhanden. Bei jedem angewendeten Preset wird automatisch ein Backup angelegt.[/dim]")
            Prompt.ask("\n[dim]Enter drücken...[/dim]")
            return

        table = Table(header_style="bold cyan", border_style="cyan")
        table.add_column("Zeitstempel", style="cyan")
        table.add_column("Datei", style="bold white")
        table.add_column("Tag", style="magenta")
        table.add_column("Pfad", style="dim")

        for b in backups[:10]:
            table.add_row(b.timestamp_human, Path(b.target_path).name, b.tag, b.target_path)

        console.print(table)
        console.print("\n[cyan][1][/cyan] Letztes Backup wiederherstellen (Rollback)")
        console.print("[dim][b] Zurück zum Hauptmenü[/dim]\n")
        choice = Prompt.ask("[bold blue]>[/bold blue] Auswahl", choices=["1", "b", "B"])
        if choice == "1":
            ok, msg = BackupManager.restore_latest()
            if ok:
                console.print(f"\n[bold green]✔ {msg}[/bold green]")
            else:
                console.print(f"\n[bold red]❌ {msg}[/bold red]")
            Prompt.ask("\n[dim]Enter drücken...[/dim]")

    def display_article(self, doc_id: str):
        if doc_id not in self.db:
            return

        doc = self.db[doc_id]
        while True:
            self.clear_screen()
            meta = (
                f"[bold cyan]Modul [{doc_id}]:[/bold cyan] [bold white]{doc.get('title', '')}[/bold white]\n"
                f"[magenta]Kategorie:[/magenta] {doc.get('category', '')}  |  "
                f"[yellow]Tags:[/yellow] {', '.join(doc.get('tags', []))}"
            )
            console.print(Panel(meta, style="cyan", expand=True))
            console.print()

            md = Markdown(doc.get("content", ""))
            console.print(md)
            console.print("\n" + "─"*60 + "\n")

            console.print("[dim][Enter] Zurück  |  [p] Terminal-Pager  |  [e] Als Markdown exportieren[/dim]")
            action = Prompt.ask("[bold blue]>[/bold blue] Aktion", choices=["", "p", "P", "e", "E"], default="")

            if action == "":
                break
            elif action.lower() == "p":
                with console.pager():
                    console.print(Panel(meta, style="cyan"))
                    console.print(md)
            elif action.lower() == "e":
                export_single_guide(doc_id, self.db)
                Prompt.ask("\n[dim]Enter drücken...[/dim]")
                break

def cli_list_guides(db):
    table = Table(title="CachyRice-Architect - Alle Ricing-Module", header_style="bold cyan")
    table.add_column("ID", style="cyan", justify="right")
    table.add_column("Kategorie", style="magenta")
    table.add_column("Titel", style="bold white")
    table.add_column("Tags", style="dim")

    for key in sorted(db.keys(), key=lambda x: int(x) if x.isdigit() else x):
        data = db[key]
        table.add_row(key, data.get("category", ""), data.get("title", ""), ", ".join(data.get("tags", [])))

    console.print(table)

def cli_list_presets():
    presets = ThemeEngine.get_presets()
    table = Table(title="🎨 CachyRice-Architect — Vorkonfigurierte Ricing-Presets", header_style="bold cyan")
    table.add_column("Kategorie", style="magenta", justify="left")
    table.add_column("Name", style="bold green")
    table.add_column("Titel", style="bold white")
    table.add_column("Ziel-Dotfile", style="cyan")
    table.add_column("Beschreibung", style="white")
    for p in presets:
        table.add_row(p.category, p.name, p.display_title, str(p.target_path), p.description)
    console.print(table)
    console.print("\n[dim]Anwenden mit: python main.py --apply <kategorie> <name>[/dim]")

def cli_apply_preset(category: str, name: str, dry_run: bool = False):
    if dry_run:
        console.print(f"[bold yellow]🔍 Simuliere Anwendung von Preset '{category}/{name}' (Dry-Run)...[/bold yellow]")
    else:
        console.print(f"[bold cyan]Wende Preset '{category}/{name}' an...[/bold cyan]")
    ok, msg = ThemeEngine.apply_preset(category, name, dry_run=dry_run)
    if ok:
        console.print(f"[bold green]{msg}[/bold green]")
    else:
        console.print(f"[bold red]{msg}[/bold red]")
        sys.exit(1)

def cli_diff_preset(category: str, name: str):
    ok, diff_text = ThemeEngine.get_diff(category, name)
    if ok:
        console.print(Panel(diff_text, title=f"🔍 Diff für Preset '{category}/{name}'", border_style="cyan"))
    else:
        console.print(f"[bold red]{diff_text}[/bold red]")
        sys.exit(1)

def cli_doctor():
    report = run_rice_doctor()
    display_rice_doctor(report)

def cli_rollback():
    console.print("[bold cyan]Führe Rollback auf das letzte Backup durch...[/bold cyan]")
    ok, msg = BackupManager.restore_latest()
    if ok:
        console.print(f"[bold green]{msg}[/bold green]")
    else:
        console.print(f"[bold red]{msg}[/bold red]")
        sys.exit(1)

def cli_list_backups():
    backups = BackupManager.list_backups()
    if not backups:
        console.print("[yellow]Keine Konfigurations-Backups vorhanden.[/yellow]")
        return
    table = Table(title="🔄 Vorhandene Dotfile-Backups", header_style="bold cyan")
    table.add_column("Datum & Uhrzeit", style="cyan")
    table.add_column("Zieldatei", style="bold white")
    table.add_column("Tag", style="magenta")
    table.add_column("Backup-Pfad", style="dim")
    for b in backups:
        table.add_row(b.timestamp_human, Path(b.target_path).name, b.tag, b.backup_file)
    console.print(table)

def main():
    parser = argparse.ArgumentParser(
        description="CachyRice-Architect Suite: Ricing & System Control für CachyOS / KDE Plasma 6 / Wayland"
    )
    parser.add_argument("-i", "--info", action="store_true", help="Zeigt Systemumgebung und Ricing-Tools Diagnose")
    parser.add_argument("-d", "--doctor", action="store_true", help="Führt eine umfassende Ricing-, Font- & Wayland-Diagnose durch")
    parser.add_argument("-l", "--list", action="store_true", help="Listet alle verfügbaren Module tabellarisch auf")
    parser.add_argument("-p", "--presets", action="store_true", help="Listet alle installierbaren Ricing-Presets auf (Starship, Fastfetch, Alacritty, Kitty, Ghostty, Konsole, Rofi, Waybar)")
    parser.add_argument("--apply", nargs=2, metavar=("CATEGORY", "NAME"), help="Wendet ein Ricing-Preset risikofrei an (z.B. --apply starship cyber-neon)")
    parser.add_argument("--diff", nargs=2, metavar=("CATEGORY", "NAME"), help="Zeigt das Diff eines Presets gegen die aktuelle Konfiguration an")
    parser.add_argument("--dry-run", action="store_true", help="Simuliert das Anwenden eines Presets ohne Dateien zu verändern")
    parser.add_argument("--rollback", action="store_true", help="Macht die letzte Ricing-Änderung rückgängig (stellt vorheriges Backup wieder her)")
    parser.add_argument("--backups", action="store_true", help="Listet alle vorhandenen Dotfile-Backups auf")
    parser.add_argument("-r", "--read", type=str, metavar="ID", help="Gibt eine bestimmte Anleitung direkt im Terminal aus")
    parser.add_argument("-s", "--search", type=str, metavar="QUERY", help="Sucht gezielt nach Begriffen in den Guides")
    parser.add_argument("-e", "--export", type=str, nargs="?", const="default", metavar="PATH", help="Exportiert alle Guides als Markdown")
    parser.add_argument("-c", "--cli", action="store_true", help="Startet das klassische Konsolen-Menü statt der Textual-TUI")
    parser.add_argument("--no-net", action="store_true", help="Deaktiviert die Online-Suche nach Aktualisierungen")

    args = parser.parse_args()

    # Direktmodi via CLI
    if args.info:
        display_system_overview()
        return

    if args.doctor:
        cli_doctor()
        return

    if args.diff:
        cli_diff_preset(args.diff[0], args.diff[1])
        return

    if args.presets:
        cli_list_presets()
        return

    if args.apply:
        cli_apply_preset(args.apply[0], args.apply[1], dry_run=args.dry_run)
        return

    if args.rollback:
        cli_rollback()
        return

    if args.backups:
        cli_list_backups()
        return

    db = load_database(DB_FILE)
    if not db:
        sys.exit(1)

    if args.list:
        cli_list_guides(db)
        return

    if args.read:
        if args.read in db:
            doc = db[args.read]
            meta = f"[bold cyan][{args.read}] {doc['category']} - {doc['title']}[/bold cyan]\n[dim]Tags: {', '.join(doc.get('tags', []))}[/dim]"
            console.print(Panel(meta, style="cyan"))
            console.print(Markdown(doc.get("content", "")))
        else:
            console.print(f"[bold red]Modul-ID '{args.read}' nicht gefunden. Verfügbar: {', '.join(db.keys())}[/bold red]")
            sys.exit(1)
        return

    if args.search:
        query = args.search.lower()
        results = [k for k, d in db.items() if query in d.get("title", "").lower() or query in d.get("content", "").lower() or query in " ".join(d.get("tags", [])).lower()]
        if not results:
            console.print(f"[red]Keine Treffer für '{args.search}'.[/red]")
        else:
            console.print(f"[bold green]{len(results)} Treffer für '{args.search}':[/bold green]\n")
            for r in results:
                console.print(f"  [cyan][{r}][/cyan] [magenta]{db[r]['category']}[/magenta] - {db[r]['title']}")
        return

    if args.export:
        target = None if args.export == "default" else args.export
        export_to_markdown(db, target)
        return

    # Klassischer CLI-Prompt-Modus falls explizit gewünscht
    if args.cli:
        try:
            app = CachyArchitectTUI(skip_network=args.no_net)
            app.run()
        except KeyboardInterrupt:
            console.print("\n[bold red]Abbruch durch Benutzer (Strg+C). Architect beendet.[/bold red]")
            sys.exit(0)
        return

    # Flaggschiff Textual TUI Modus (Standard)
    try:
        run_tui(DB_FILE)
    except Exception as e:
        console.print(f"[yellow]Warnung: Textual-TUI konnte nicht gestartet werden ({e}). Wechsle zu CLI-Modus...[/yellow]")
        try:
            app = CachyArchitectTUI(skip_network=args.no_net)
            app.run()
        except KeyboardInterrupt:
            console.print("\n[bold red]Abbruch durch Benutzer (Strg+C). Architect beendet.[/bold red]")
            sys.exit(0)

if __name__ == "__main__":
    main()

