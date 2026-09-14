import time
import urllib.request
import urllib.error
from rich.console import Console

console = Console()

def check_web_updates(timeout_sec: float = 0.5, skip: bool = True) -> bool:
    """
    Prüft online auf optionale Guide-Aktualisierungen.
    Standardmäßig wird im Offline-First Modus schnell auf die lokale Datenbank zugegriffen.
    """
    if skip:
        return False

    try:
        req = urllib.request.Request(
            "https://raw.githubusercontent.com/cachyos/wiki/main/README.md",
            headers={"User-Agent": "CachyRice-Architect/2.0"}
        )
        with urllib.request.urlopen(req, timeout=timeout_sec) as response:
            return response.status == 200
    except Exception:
        return False

