from dataclasses import dataclass, asdict
from pathlib import Path
import json
from datetime import datetime
from typing import Optional


@dataclass
class Project:
    name: str
    path: Path
    description: str = ""
    stats: Optional[dict] = None

    created_at: Optional[str] = None
    last_modified: Optional[str] = None

    def save_to_json(self, json_file: Optional[Path] = None) -> None:
        """Speichert Projektdaten als JSON-Datei im Projektordner."""
        if json_file is None:
            json_file = self.path / f"{self.path.name}.json"

        now = datetime.now().isoformat()

        if self.created_at is None:
            self.created_at = now
        self.last_modified = now

        data = asdict(self)
        data["path"] = str(self.path)

        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        print(f"Saved project JSON at {json_file}")

    @classmethod
    def load_from_json(cls, folder: Path, json_file: Optional[Path] = None) -> "Project":
        """Lädt ein Projekt aus seiner JSON-Datei oder erstellt ein neues."""
        if json_file is None:
            json_file = folder / f"{folder.name}.json"

        if not json_file.exists():
            return cls(name=folder.name, path=folder)

        with open(json_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return cls(
            name=data.get("name", folder.name),
            path=Path(data.get("path", folder)),
            description=data.get("description", ""),
            stats=data.get("stats"),
            created_at=data.get("created_at"),
            last_modified=data.get("last_modified"),
        )
