"""Resolve paths strictly inside For Reviewer/."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "source_data"
ILLUSTRATIONS = ROOT / "illustrations"
OUTPUT_FIG = ROOT / "outputs" / "figures"
OUTPUT_DATA = ROOT / "outputs" / "source_data"
NOTEBOOKS = ROOT / "notebooks"


def require(path: Path) -> Path:
    if not path.exists():
        raise FileNotFoundError(
            f"Required data not found: {path}\n"
            f"Run: python setup/copy_and_extract_data.py from For Reviewer/"
        )
    return path


def source(name: str) -> Path:
    return require(SOURCE / name)


def illustration_dir(panel_id: str) -> Path:
    return ILLUSTRATIONS / panel_id


def ensure_output_dirs() -> None:
    OUTPUT_FIG.mkdir(parents=True, exist_ok=True)
    OUTPUT_DATA.mkdir(parents=True, exist_ok=True)
