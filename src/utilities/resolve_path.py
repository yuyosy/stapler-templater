import sys
from pathlib import Path


def resolve_path(*pathes: str | Path) -> Path:
    if hasattr(sys, "_MEIPASS"):
        # If running as a PyInstaller bundle, use the _MEIPASS directory
        base_path = Path(sys.argv[0]).absolute().parent
    else:
        # Otherwise, use the current working directory
        base_path = Path.cwd()
    return base_path.joinpath(*pathes)
