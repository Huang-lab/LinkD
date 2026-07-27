#!/usr/bin/env python3
"""Build the deterministic notebook-first Zenodo reproduction archive."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
import zipfile
import shutil
from pathlib import Path, PurePosixPath

import pandas as pd

REPO = Path(__file__).resolve().parents[1]
PAYLOAD = REPO / "build" / "reviewer_bundle"
DEFAULT_OUTPUT = REPO / "zenodo_upload" / "LinkD_Figure_Reproduction_Data.zip"
OBSOLETE = REPO / "zenodo_upload" / "For_Reviewer_large_data.zip"
FIXED_TIME = (1980, 1, 1, 0, 0, 0)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while block := handle.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def refresh_panel_manifest() -> None:
    data = PAYLOAD / "data"
    installed_data = REPO / "For_Reviewer" / "data"
    installed_static = REPO / "For_Reviewer" / "static"
    if not data.is_dir() and installed_data.is_dir():
        shutil.copytree(installed_data, data)
    if not (PAYLOAD / "static").is_dir() and installed_static.is_dir():
        shutil.copytree(installed_static, PAYLOAD / "static")
    extracted = REPO / "build" / "reviewer_source" / "panels"
    if extracted.is_dir():
        data.mkdir(parents=True, exist_ok=True)
        for path in extracted.glob("*.csv"):
            shutil.copy2(path, data / path.name)
    panel_files = sorted(data.glob("*.csv"))
    panel_files = [path for path in panel_files if path.name != "manifest.csv"]
    expected = {
        "fig1b", "fig1c", "fig2a", "fig2b", "fig2cd", "fig2e", "fig2f",
        "fig2g", "fig3b", "fig3c", "fig3pairs", "fig3f", "fig3g",
        "fig3h_edges", "fig4b_nodes", "fig4b_edges", "fig5a", "fig5d",
        "fig5ef", "fig5g", "fig5hi", "fig5j", "fig5k", "figs2",
        "figs3s4", "figs5ab", "figs5cd",
    }
    if {path.stem for path in panel_files} != expected:
        raise RuntimeError("Author payload does not contain exactly the 27 required panel tables")

    old_manifest_path = REPO / "For_Reviewer" / "source_data" / "manifest.json"
    old_by_name = {}
    if old_manifest_path.is_file():
        old_by_name = {
            Path(entry["path"]).name: entry
            for entry in json.loads(old_manifest_path.read_text(encoding="utf-8"))
        }

    entries = []
    for path in panel_files:
        frame = pd.read_csv(path)
        old = old_by_name.get(path.name, {})
        entries.append({
            "path": path.name,
            "sha256": sha256_file(path),
            "bytes": path.stat().st_size,
            "rows": len(frame),
            "columns": list(frame.columns),
            "origin": old.get("origin", "author analysis source and submitted manuscript tables"),
            "transformation": old.get("transformation", "deterministic panel-table extraction"),
            "panels": old.get("panels", path.stem),
            "privacy": "aggregate/non-identifiable",
        })
    (data / "manifest.json").write_text(
        json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    flat = pd.DataFrame(entries)
    flat["columns"] = flat["columns"].map(json.dumps)
    flat.to_csv(data / "manifest.csv", index=False, lineterminator="\n")


def validate_payload() -> None:
    refresh_panel_manifest()
    command = [
        sys.executable,
        str(REPO / "scripts" / "reviewer_data" / "validate_package.py"),
        "--data-dir", str(PAYLOAD / "data"),
        "--skip-outputs",
    ]
    subprocess.run(command, cwd=REPO, check=True)
    if not (PAYLOAD / "static").is_dir():
        raise FileNotFoundError(PAYLOAD / "static")


def payload_files() -> list[tuple[str, Path]]:
    files = []
    for root_name in ("data", "static"):
        root = PAYLOAD / root_name
        for path in root.rglob("*"):
            if path.is_file():
                files.append((path.relative_to(PAYLOAD).as_posix(), path))
    return sorted(files)


def zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, FIXED_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.create_system = 3
    info.external_attr = 0o100644 << 16
    return info


def safe_member(name: str) -> bool:
    path = PurePosixPath(name)
    return bool(name) and not path.is_absolute() and ".." not in path.parts


def verify_archive(path: Path) -> None:
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        if len(names) != len(set(names)) or not all(safe_member(name) for name in names):
            raise RuntimeError("Archive has duplicate or unsafe paths")
        manifest = json.loads(archive.read("BUNDLE_MANIFEST.json"))
        expected = {entry["path"]: entry for entry in manifest["files"]}
        if set(names) != set(expected) | {"BUNDLE_MANIFEST.json"}:
            raise RuntimeError("Bundle manifest does not match archive members")
        for name, entry in expected.items():
            data = archive.read(name)
            if len(data) != entry["bytes"] or sha256_bytes(data) != entry["sha256"]:
                raise RuntimeError(f"Archive verification failed: {name}")


def build_archive(output: Path) -> None:
    files = payload_files()
    manifest = {
        "schema_version": 1,
        "files": [
            {"path": name, "sha256": sha256_file(path), "bytes": path.stat().st_size}
            for name, path in files
        ],
    }
    manifest_bytes = (
        json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=output.name + ".", suffix=".tmp", dir=output.parent, delete=False
    ) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(
            temporary, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9
        ) as archive:
            archive.writestr(zip_info("BUNDLE_MANIFEST.json"), manifest_bytes)
            for name, path in files:
                archive.writestr(zip_info(name), path.read_bytes())
        verify_archive(temporary)
        temporary.replace(output)
        os.chmod(output, 0o644)
    finally:
        temporary.unlink(missing_ok=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--keep-obsolete", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output.resolve()
    if args.verify_only:
        verify_archive(output)
        print(f"Verified {output}")
        return 0
    validate_payload()
    build_archive(output)
    digest = sha256_file(output)
    if not args.keep_obsolete and OBSOLETE.exists() and OBSOLETE.resolve() != output:
        OBSOLETE.unlink()
    print(f"Built: {output}")
    print(f"SHA-256: {digest}")
    print(f"Bytes: {output.stat().st_size}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
