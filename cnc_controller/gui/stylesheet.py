from pathlib import Path

THEMES_DIR = Path(__file__).parent.parent.parent / "themes"


def load_stylesheet(name: str = "stylesheet.qss") -> str:
    path = THEMES_DIR / name
    if path.exists():
        return path.read_text(encoding="utf-8")
    return ""
