#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from typing import Dict, Any, List, Optional

from textual.app import App, ComposeResult
from textual.containers import Vertical, Horizontal, Container, ScrollableContainer
from textual.widgets import Header, Footer, Input, Label, Button, OptionList, Markdown, Select, Static, Rule
from textual.widgets.option_list import Option
from textual.screen import ModalScreen
from textual.binding import Binding
from textual import on

from modules.storage import (
    load_database,
    export_single_guide,
    export_to_markdown,
    get_categories,
    get_all_tags,
)
from modules.system_info import get_full_system_data


class SystemDiagnosticModal(ModalScreen[None]):
    """Modal zur Anzeige detaillierter System- und Tool-Status."""
    
    DEFAULT_CSS = """
    SystemDiagnosticModal {
        align: center middle;
        background: rgba(17, 17, 27, 0.85);
    }
    #diag-box {
        width: 84;
        height: 85%;
        background: #1e1e2e;
        border: heavy #89dceb;
        padding: 1 2;
    }
    #diag-title {
        text-align: center;
        text-style: bold;
        color: #89dceb;
        margin-bottom: 1;
    }
    .diag-section {
        color: #f9e2af;
        text-style: bold;
        margin-top: 1;
        margin-bottom: 0;
    }
    .diag-item {
        color: #cdd6f4;
        padding-left: 2;
    }
    .installed {
        color: #a6e3a1;
        text-style: bold;
    }
    .missing {
        color: #f38ba8;
    }
    #diag-close-btn {
        margin-top: 1;
        width: 100%;
        background: #313244;
        color: #cdd6f4;
    }
    #diag-close-btn:hover {
        background: #45475a;
        color: #89dceb;
    }
    """

    BINDINGS = [
        Binding("escape", "dismiss_modal", "Schließen"),
        Binding("q", "dismiss_modal", "Schließen"),
    ]

    def compose(self) -> ComposeResult:
        sys_data = get_full_system_data()
        with Vertical(id="diag-box"):
            yield Label("⚡ System-Diagnose & Ricing-Tools Check", id="diag-title")
            with ScrollableContainer(id="diag-content"):
                yield Label("Systemumgebung:", classes="diag-section")
                yield Label(f"• Distribution: {sys_data['distro']}", classes="diag-item")
                yield Label(f"• Kernel: {sys_data['kernel']}", classes="diag-item")
                yield Label(f"• Desktop-Umgebung: {sys_data['desktop']}", classes="diag-item")
                yield Label(f"• Sitzungstyp: {sys_data['session_type']}", classes="diag-item")
                yield Label(f"• Shell: {sys_data['shell']}", classes="diag-item")
                yield Label(f"• Prozessor: {sys_data['cpu']}", classes="diag-item")
                
                yield Rule()
                yield Label("Installierte Ricing-Komponenten:", classes="diag-section")
                
                tools = sys_data.get("tools", {})
                for cat, tool_list in tools.items():
                    yield Label(f"[{cat}]", classes="diag-section")
                    for t in tool_list:
                        status_str = "✔ Installiert" if t["installed"] else "✖ Fehlt"
                        cls = "installed" if t["installed"] else "missing"
                        path_str = f" ({t['path']})" if t["installed"] else ""
                        yield Label(f"  • {t['label']}: [{status_str}]{path_str}", classes=f"diag-item {cls}")
            
            yield Button("Schließen [Esc / q]", id="diag-close-btn", variant="primary")

    def action_dismiss_modal(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#diag-close-btn")
    def on_close(self) -> None:
        self.dismiss(None)


class ExportConfirmModal(ModalScreen[Optional[str]]):
    """Modal zur Auswahl des Speicherorts für den Markdown-Export."""
    
    DEFAULT_CSS = """
    ExportConfirmModal {
        align: center middle;
        background: rgba(17, 17, 27, 0.85);
    }
    #export-box {
        width: 70;
        height: auto;
        background: #1e1e2e;
        border: heavy #a6e3a1;
        padding: 1 2;
    }
    #export-title {
        text-align: center;
        text-style: bold;
        color: #a6e3a1;
        margin-bottom: 1;
    }
    #export-path-input {
        margin: 1 0;
    }
    #export-buttons {
        height: auto;
        align: right middle;
    }
    #export-buttons Button {
        margin-left: 1;
    }
    """

    def __init__(self, title: str, default_path: str):
        super().__init__()
        self.title_text = title
        self.default_path = default_path

    def compose(self) -> ComposeResult:
        with Vertical(id="export-box"):
            yield Label(self.title_text, id="export-title")
            yield Label("Dateipfad bestätigen:")
            yield Input(value=self.default_path, id="export-path-input")
            with Horizontal(id="export-buttons"):
                yield Button("Abbrechen", variant="error", id="btn-cancel")
                yield Button("Exportieren", variant="success", id="btn-export-ok")

    def on_mount(self) -> None:
        self.query_one("#export-path-input", Input).focus()

    @on(Button.Pressed, "#btn-cancel")
    def on_cancel(self) -> None:
        self.dismiss(None)

    @on(Button.Pressed, "#btn-export-ok")
    def on_ok(self) -> None:
        val = self.query_one("#export-path-input", Input).value.strip()
        self.dismiss(val if val else self.default_path)


class CachyRiceApp(App):
    """
    Flaggschiff TUI für den CachyRice-Architect:
    Interaktives Nachschlagewerk, Live-Filter, Markdown-Renderer, System-Auditor.
    """
    TITLE = "⚡ CachyRice-Architect"
    SUB_TITLE = "CachyOS / KDE Plasma 6 / Wayland Ricing Suite"

    CSS = """
    Screen {
        background: #11111b;
        color: #cdd6f4;
    }
    
    #top-meta-bar {
        height: 2;
        background: #181825;
        color: #89dceb;
        padding: 0 1;
        content-align: center middle;
        border-bottom: solid #313244;
    }
    
    #main-layout {
        height: 1fr;
    }
    
    #left-panel {
        width: 38;
        background: #181825;
        border-right: solid #313244;
        height: 100%;
        padding: 0 1;
    }
    
    .panel-heading {
        color: #89dceb;
        text-style: bold;
        padding: 1 0 0 0;
    }
    
    #search-box {
        margin: 0 0 1 0;
        background: #1e1e2e;
        border: tall #45475a;
        color: #cdd6f4;
    }
    #search-box:focus {
        border: tall #89dceb;
    }
    
    #category-select {
        margin-bottom: 1;
        background: #1e1e2e;
        border: tall #45475a;
    }
    
    #guide-list {
        height: 1fr;
        background: #11111b;
        border: solid #313244;
    }
    
    .guide-item {
        padding: 0 1;
        height: 2;
        color: #cdd6f4;
    }
    .guide-item:hover {
        background: #313244;
        color: #89dceb;
    }
    .guide-item-selected {
        background: #45475a;
        color: #a6e3a1;
        text-style: bold;
    }
    .item-id {
        color: #f9e2af;
        text-style: bold;
    }
    .item-cat {
        color: #cba6f7;
        text-style: italic;
    }
    
    #center-panel {
        width: 1fr;
        height: 100%;
        background: #1e1e2e;
        padding: 0 1;
    }
    
    #guide-header-card {
        height: 3;
        background: #181825;
        border-bottom: solid #89dceb;
        padding: 0 1;
        align: left middle;
    }
    
    #guide-title {
        text-style: bold;
        color: #89dceb;
    }
    
    #guide-meta {
        color: #a6adc8;
    }
    
    #markdown-container {
        height: 1fr;
        background: #1e1e2e;
        padding: 1;
    }
    
    #action-bar {
        height: 3;
        background: #181825;
        border-top: solid #313244;
        align: right middle;
        padding: 0 1;
    }
    #action-bar Button {
        margin-left: 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Beenden", priority=True),
        Binding("escape", "quit", "Beenden"),
        Binding("/", "focus_search", "Suchen"),
        Binding("s", "focus_search", "Suchen"),
        Binding("e", "export_current", "Export (Guide)"),
        Binding("f3", "export_all", "Gesamtexport"),
        Binding("d", "show_diagnostics", "System-Diagnose"),
        Binding("f5", "reset_filter", "Reset"),
        Binding("1", "jump_to_guide('1')", "Guide 1", show=False),
        Binding("2", "jump_to_guide('2')", "Guide 2", show=False),
        Binding("3", "jump_to_guide('3')", "Guide 3", show=False),
        Binding("4", "jump_to_guide('4')", "Guide 4", show=False),
        Binding("5", "jump_to_guide('5')", "Guide 5", show=False),
        Binding("6", "jump_to_guide('6')", "Guide 6", show=False),
        Binding("7", "jump_to_guide('7')", "Guide 7", show=False),
        Binding("8", "jump_to_guide('8')", "Guide 8", show=False),
        Binding("9", "jump_to_guide('9')", "Guide 9", show=False),
    ]

    def __init__(self, db_path: Optional[str] = None):
        super().__init__()
        self.db_path = db_path or os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "guides.json")
        self.db = load_database(self.db_path)
        self.active_id: Optional[str] = "1" if "1" in self.db else (list(self.db.keys())[0] if self.db else None)
        self.current_filtered_keys: List[str] = list(self.db.keys())
        self.categories = get_categories(self.db)
        self.selected_category: str = "ALL"

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        
        # Meta bar
        sys_data = get_full_system_data()
        meta_text = (
            f"⚡ [bold cyan]Kernel:[/bold cyan] {sys_data['kernel']}  │  "
            f"[bold cyan]Desktop:[/bold cyan] {sys_data['desktop']} ({sys_data['session_type']})  │  "
            f"[bold cyan]Shell:[/bold cyan] {sys_data['shell'].split('/')[-1]}  │  "
            f"[bold cyan]Guides:[/bold cyan] {len(self.db)}"
        )
        yield Static(meta_text, id="top-meta-bar")

        with Horizontal(id="main-layout"):
            # Left panel
            with Vertical(id="left-panel"):
                yield Label("🔍 Filter & Suche (Taste: /)", classes="panel-heading")
                yield Input(placeholder="Suchbegriff (Titel, Tag, Text)...", id="search-box")
                
                cat_options = [("Alle Kategorien", "ALL")] + [(c, c) for c in sorted(self.categories.keys())]
                yield Select(options=cat_options, value="ALL", id="category-select", allow_blank=False)
                
                yield Label("📚 Verfügbare Guides:", classes="panel-heading")
                yield OptionList(id="guide-list")

            # Center panel
            with Vertical(id="center-panel"):
                with Vertical(id="guide-header-card"):
                    yield Label("Titel", id="guide-title")
                    yield Label("Kategorie & Schlagwörter", id="guide-meta")
                
                with ScrollableContainer(id="markdown-container"):
                    yield Markdown("", id="guide-markdown")
                
                with Horizontal(id="action-bar"):
                    yield Button("System-Diagnose [d]", variant="default", id="btn-diag")
                    yield Button("Gesamtexport [F3]", variant="warning", id="btn-export-all")
                    yield Button("Guide exportieren [e]", variant="success", id="btn-export-one")

        yield Footer()

    async def on_mount(self) -> None:
        self.populate_guide_list()
        if self.active_id:
            await self.display_guide(self.active_id)

    def populate_guide_list(self) -> None:
        opt_list = self.query_one("#guide-list", OptionList)
        opt_list.clear_options()

        sorted_keys = sorted(self.current_filtered_keys, key=lambda x: int(x) if x.isdigit() else x)
        for key in sorted_keys:
            doc = self.db.get(key, {})
            title = doc.get("title", f"Guide {key}")
            cat = doc.get("category", "")
            prompt = f"[{key}] {title} ({cat})"
            opt_list.add_option(Option(prompt, id=key))

    async def display_guide(self, doc_id: str) -> None:
        if doc_id not in self.db:
            return
        self.active_id = doc_id
        doc = self.db[doc_id]

        title_lbl = self.query_one("#guide-title", Label)
        meta_lbl = self.query_one("#guide-meta", Label)
        md_view = self.query_one("#guide-markdown", Markdown)

        title_lbl.update(f"⚡ [{doc_id}] {doc.get('title', '')}")
        tags_str = ", ".join([f"#{t}" for t in doc.get("tags", [])])
        meta_lbl.update(f"Kategorie: {doc.get('category', '')}  |  Tags: {tags_str}")

        content = doc.get("content", "*Kein Inhalt vorhanden.*")
        await md_view.update(content)

    @on(OptionList.OptionSelected, "#guide-list")
    async def on_guide_selected(self, event: OptionList.OptionSelected) -> None:
        if event.option_id:
            await self.display_guide(str(event.option_id))

    @on(OptionList.OptionHighlighted, "#guide-list")
    async def on_guide_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        if event.option_id:
            await self.display_guide(str(event.option_id))

    @on(Input.Changed, "#search-box")
    def on_search_changed(self, event: Input.Changed) -> None:
        query = event.value.strip().lower()
        self.apply_filter(query, self.selected_category)

    @on(Select.Changed, "#category-select")
    def on_category_changed(self, event: Select.Changed) -> None:
        self.selected_category = str(event.value)
        search_query = self.query_one("#search-box", Input).value.strip().lower()
        self.apply_filter(search_query, self.selected_category)

    def apply_filter(self, query: str, category: str) -> None:
        filtered = []
        for key, doc in self.db.items():
            cat = doc.get("category", "")
            if category != "ALL" and cat != category:
                continue

            if not query:
                filtered.append(key)
                continue

            title = doc.get("title", "").lower()
            content = doc.get("content", "").lower()
            tags = " ".join(doc.get("tags", [])).lower()

            if query in title or query in content or query in tags or query in cat.lower():
                filtered.append(key)

        self.current_filtered_keys = filtered
        self.populate_guide_list()

    def action_focus_search(self) -> None:
        self.query_one("#search-box", Input).focus()

    def action_reset_filter(self) -> None:
        search_box = self.query_one("#search-box", Input)
        search_box.value = ""
        cat_select = self.query_one("#category-select", Select)
        cat_select.value = "ALL"
        self.selected_category = "ALL"
        self.current_filtered_keys = list(self.db.keys())
        self.populate_guide_list()
        self.notify("Filter zurückgesetzt.", severity="information")

    def action_show_diagnostics(self) -> None:
        self.push_screen(SystemDiagnosticModal())

    @on(Button.Pressed, "#btn-diag")
    def on_diag_btn(self) -> None:
        self.action_show_diagnostics()

    def action_export_current(self) -> None:
        if not self.active_id or self.active_id not in self.db:
            self.notify("Kein aktiver Guide zum Exportieren ausgewählt.", severity="warning")
            return

        doc = self.db[self.active_id]
        slug = doc["title"].lower().replace(" ", "_").replace("/", "_").replace("(", "").replace(")", "")
        default_path = os.path.expanduser(f"~/cachy_guide_{self.active_id}_{slug}.md")

        def handle_export(path: Optional[str]) -> None:
            if path:
                success = export_single_guide(self.active_id, self.db, path)
                if success:
                    self.notify(f"Guide exportiert nach:\n{path}", title="Export Erfolgreich", timeout=6)
                else:
                    self.notify("Fehler beim Exportieren!", severity="error")

        self.push_screen(
            ExportConfirmModal(f"Guide [{self.active_id}] exportieren", default_path),
            handle_export
        )

    @on(Button.Pressed, "#btn-export-one")
    def on_export_current_btn(self) -> None:
        self.action_export_current()

    def action_export_all(self) -> None:
        default_path = os.path.expanduser("~/cachy_rice_guide_komplett.md")

        def handle_export_all(path: Optional[str]) -> None:
            if path:
                success = export_to_markdown(self.db, path)
                if success:
                    self.notify(f"Gesamtdokumentation exportiert nach:\n{path}", title="Export Erfolgreich", timeout=6)
                else:
                    self.notify("Fehler beim Gesamtexport!", severity="error")

        self.push_screen(
            ExportConfirmModal("Gesamtdokumentation exportieren", default_path),
            handle_export_all
        )

    @on(Button.Pressed, "#btn-export-all")
    def on_export_all_btn(self) -> None:
        self.action_export_all()

    def action_jump_to_guide(self, guide_id: str) -> None:
        if guide_id in self.db:
            self.run_worker(self.display_guide(guide_id))
            self.notify(f"Zu Guide [{guide_id}] gewechselt.")


def run_tui(db_path: Optional[str] = None) -> None:
    """Startet die interaktive Textual TUI."""
    app = CachyRiceApp(db_path=db_path)
    app.run()
