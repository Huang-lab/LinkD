#!/usr/bin/env python3
"""Fast CI checks for public DOI, documentation links, and obvious secrets."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path
from urllib.parse import unquote


ROOT = Path(__file__).resolve().parents[1]
CANONICAL_DOI = "https://doi.org/10.5281/zenodo.19241151"
PUBLIC_DOCS = (
    ROOT / "README.md",
    ROOT / "METHODS.md",
    ROOT / "RESULTS.md",
    ROOT / "CHANGELOG.md",
    ROOT / "For_Reviewer" / "README.md",
    ROOT / "docs" / "FOR_REVIEWER.md",
    ROOT / "benchmark" / "README.md",
    ROOT / "benchmark" / "RERUN.md",
    ROOT / "benchmark" / "TASK_CATALOG.md",
)
SECRET_PATTERNS = {
    "OpenAI key": re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    "Anthropic key": re.compile(r"\bsk-ant-[A-Za-z0-9_-]{20,}\b"),
    "Google API key": re.compile(r"\bAIza[A-Za-z0-9_-]{30,}\b"),
    "Private key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def tracked_files() -> list[Path]:
    output = subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT
    ).decode("utf-8", errors="strict")
    return [ROOT / name for name in output.rstrip("\0").split("\0") if name]


def text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return None


def check_doi(files: list[Path]) -> list[str]:
    errors: list[str] = []
    obsolete_record = "216" + "15191"
    mistyped_concept = "1924115" + "2"
    forbidden = (
        f"zenodo.{obsolete_record}",
        f"zenodo.{mistyped_concept}",
        f"/records/{obsolete_record}",
    )
    for path in files:
        if path == ROOT / "For_Reviewer" / "notebooks" / "Data_Preparation.ipynb":
            # Saved output may report the immutable version DOI resolved at runtime.
            continue
        content = text(path)
        if content is None:
            continue
        for value in forbidden:
            if value in content:
                errors.append(f"{path.relative_to(ROOT)} contains stale LinkD reference {value}")
    for path in (ROOT / "README.md", ROOT / "For_Reviewer" / "README.md"):
        if CANONICAL_DOI not in path.read_text(encoding="utf-8"):
            errors.append(f"{path.relative_to(ROOT)} is missing the canonical concept DOI")
    return errors


def check_relative_links() -> list[str]:
    errors: list[str] = []
    pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    for path in PUBLIC_DOCS:
        content = path.read_text(encoding="utf-8")
        for raw in pattern.findall(content):
            target = raw.strip().strip("<>")
            if (
                not target
                or target.startswith(("http://", "https://", "mailto:", "#"))
            ):
                continue
            target = unquote(target.split("#", 1)[0])
            if not target:
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(
                    f"{path.relative_to(ROOT)} has broken relative link: {raw}"
                )
    return errors


def check_secrets(files: list[Path]) -> list[str]:
    errors: list[str] = []
    for path in files:
        content = text(path)
        if content is None:
            continue
        for label, pattern in SECRET_PATTERNS.items():
            if pattern.search(content):
                errors.append(f"{path.relative_to(ROOT)} may contain a {label}")
    return errors


def main() -> int:
    files = tracked_files()
    errors = check_doi(files) + check_relative_links() + check_secrets(files)
    if errors:
        print("Repository consistency checks failed:")
        for error in errors:
            print(f"  - {error}")
        return 1
    print("Repository consistency checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
