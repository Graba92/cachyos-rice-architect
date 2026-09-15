# -*- coding: utf-8 -*-
"""
modules/backup_manager.py — Zerstörungsfreier Backup & Rollback Manager
Sichert Konfigurationsdateien vor Änderungen und ermöglicht 1-Klick Rollbacks.
"""

from __future__ import annotations
import json
import shutil
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

BACKUP_ROOT = Path.home() / ".config" / "cachyos-rice-architect" / "backups"
MANIFEST_FILE = BACKUP_ROOT / "manifest.json"


@dataclass
class BackupRecord:
    backup_id: str
    timestamp: float
    timestamp_human: str
    target_path: str
    backup_file: str
    tag: str


class BackupManager:
    """Verwaltet Zeitstempel-Backups für Konfigurationsdateien."""

    @classmethod
    def _load_manifest(cls) -> List[Dict]:
        if not MANIFEST_FILE.exists():
            return []
        try:
            with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []

    @classmethod
    def _save_manifest(cls, data: List[Dict]) -> None:
        BACKUP_ROOT.mkdir(parents=True, exist_ok=True)
        try:
            with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception:
            pass

    @classmethod
    def backup_file(cls, target_path: Path, tag: str = "preset_apply") -> Tuple[bool, Optional[str]]:
        """Erstellt eine Sicherheitskopie einer bestehenden Konfigurationsdatei."""
        if not target_path.exists():
            return True, None  # Keine bestehende Datei, kein Backup nötig

        ts = time.time()
        ts_str = time.strftime("%Y%m%d_%H%M%S", time.localtime(ts))
        backup_id = f"{target_path.name}.{ts_str}"
        dest_dir = BACKUP_ROOT / ts_str
        dest_dir.mkdir(parents=True, exist_ok=True)
        dest_file = dest_dir / target_path.name

        try:
            shutil.copy2(target_path, dest_file)
            manifest = cls._load_manifest()
            manifest.append({
                "backup_id": backup_id,
                "timestamp": ts,
                "timestamp_human": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(ts)),
                "target_path": str(target_path.resolve()),
                "backup_file": str(dest_file.resolve()),
                "tag": tag
            })
            cls._save_manifest(manifest)
            return True, backup_id
        except Exception as e:
            return False, str(e)

    @classmethod
    def list_backups(cls) -> List[BackupRecord]:
        """Gibt alle registrierten Backups chronologisch zurück."""
        raw = cls._load_manifest()
        records = []
        for item in reversed(raw):
            records.append(BackupRecord(
                backup_id=item.get("backup_id", ""),
                timestamp=item.get("timestamp", 0.0),
                timestamp_human=item.get("timestamp_human", ""),
                target_path=item.get("target_path", ""),
                backup_file=item.get("backup_file", ""),
                tag=item.get("tag", "")
            ))
        return records

    @classmethod
    def restore_latest(cls) -> Tuple[bool, str]:
        """Stellt das zuletzt erstellte Backup wieder her."""
        backups = cls.list_backups()
        if not backups:
            return False, "Keine Backups vorhanden."

        latest = backups[0]
        backup_src = Path(latest.backup_file)
        target_dest = Path(latest.target_path)

        if not backup_src.exists():
            return False, f"Backup-Datei {backup_src} existiert nicht mehr auf dem Datenträger."

        try:
            target_dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(backup_src, target_dest)
            return True, f"Erfolgreich wiederhergestellt: {target_dest.name} aus Stand {latest.timestamp_human}"
        except Exception as e:
            return False, f"Fehler beim Wiederherstellen: {e}"
