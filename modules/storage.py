import os
import json
from typing import Dict, List, Any, Optional
from rich.console import Console
from rich.prompt import Prompt

console = Console()

def load_database(filepath: str = "data/guides.json") -> Dict[str, Any]:
    """Lädt die Guides-JSON-Datenbank mit UTF-8 Kodierung."""
    if not os.path.isabs(filepath):
        # Relativ zum Projektverzeichnis auflösen
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        candidate = os.path.join(base_dir, filepath)
        if os.path.exists(candidate):
            filepath = candidate

    if not os.path.exists(filepath):
        console.print(f"[bold red]Kritischer Fehler: {filepath} nicht gefunden![/bold red]")
        return {}
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        console.print(f"[bold red]Fehler: guides.json ist korrupt: {e}[/bold red]")
        return {}
    except Exception as e:
        console.print(f"[bold red]Fehler beim Lesen der Datenbank: {e}[/bold red]")
        return {}

def get_categories(db: Dict[str, Any]) -> Dict[str, List[str]]:
    """Gruppiert Modul-IDs nach Kategorien."""
    categories: Dict[str, List[str]] = {}
    for key, data in db.items():
        cat = data.get("category", "Allgemein")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append(key)
    return categories

def get_all_tags(db: Dict[str, Any]) -> Dict[str, List[str]]:
    """Erstellt einen Index von Tags zu zugehörigen Modul-IDs."""
    tags_index: Dict[str, List[str]] = {}
    for key, data in db.items():
        tags = data.get("tags", [])
        for tag in tags:
            tag_clean = tag.strip().lower()
            if tag_clean not in tags_index:
                tags_index[tag_clean] = []
            if key not in tags_index[tag_clean]:
                tags_index[tag_clean].append(key)
    return tags_index

def export_single_guide(doc_id: str, db: Dict[str, Any], export_path: Optional[str] = None) -> bool:
    """Exportiert eine einzelne Anleitung als Markdown-Datei."""
    if doc_id not in db:
        console.print(f"[red]Modul ID {doc_id} nicht gefunden.[/red]")
        return False

    doc = db[doc_id]
    slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
    default_path = os.path.expanduser(f"~/cachy_guide_{doc_id}_{slug}.md")

    if not export_path:
        export_path = Prompt.ask("[bold yellow]Speicherort für Einzel-Export[/bold yellow]", default=default_path)

    export_path = os.path.expanduser(export_path)
    export_dir = os.path.dirname(export_path)
    if export_dir and not os.path.exists(export_dir):
        try:
            os.makedirs(export_dir, exist_ok=True)
        except Exception as e:
            console.print(f"[bold red]Fehler beim Erstellen des Verzeichnisses: {e}[/bold red]")
            return False

    content = f"# {doc['category']} - {doc['title']}\n\n"
    content += f"*Tags: {', '.join(doc.get('tags', []))}*\n\n"
    content += doc.get("content", "").strip() + "\n"

    try:
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"\n[bold green]✔ Guide erfolgreich exportiert nach:[/bold green] [white]{export_path}[/white]")
        return True
    except Exception as e:
        console.print(f"\n[bold red]✖ Fehler beim Exportieren: {e}[/bold red]")
        return False

def export_to_markdown(db: Dict[str, Any], export_path: Optional[str] = None) -> bool:
    """Exportiert alle Anleitungen der Datenbank in eine zusammenhängende Markdown-Datei."""
    default_path = os.path.expanduser("~/cachy_rice_guide_komplett.md")
    if not export_path:
        export_path = Prompt.ask("[bold yellow]Speicherort für Gesamtexport (Markdown)[/bold yellow]", default=default_path)
    
    export_path = os.path.expanduser(export_path)
    export_dir = os.path.dirname(export_path)
    if export_dir and not os.path.exists(export_dir):
        try:
            os.makedirs(export_dir, exist_ok=True)
        except Exception as e:
            console.print(f"[bold red]Fehler beim Erstellen des Verzeichnisses: {e}[/bold red]")
            return False

    md_content = "# CachyRice-Architect - Gesamtdokumentation\n\n"
    md_content += "> Umfassender Leitfaden für Ricing, Performance und UI-Konfiguration unter CachyOS (KDE Plasma 6 / Wayland / TUI).\n\n"
    md_content += "---\n\n"

    for key, data in sorted(db.items(), key=lambda x: int(x[0]) if x[0].isdigit() else x[0]):
        md_content += f"## [{key}] {data.get('category', 'Allgemein')} - {data.get('title', 'Ohne Titel')}\n"
        md_content += f"**Schlagwörter:** `{', '.join(data.get('tags', []))}`\n\n"
        md_content += data.get("content", "").strip() + "\n\n---\n\n"

    try:
        with open(export_path, "w", encoding="utf-8") as f:
            f.write(md_content)
        console.print(f"\n[bold green]✔ Gesamtdokumentation erfolgreich exportiert nach:[/bold green] [white]{export_path}[/white]")
        return True
    except Exception as e:
        console.print(f"\n[bold red]✖ Unerwarteter Fehler: {e}[/bold red]")
        return False
