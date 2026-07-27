"""Download and verify the LinkD application datasets from Zenodo.

The public data reference is the stable concept DOI:
https://doi.org/10.5281/zenodo.19241151

The script resolves that concept record to its latest published version, checks
Zenodo's checksum for each expected archive, validates ZIP member paths, and
installs the five dataset directories atomically.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import stat
import sys
import tempfile
import urllib.error
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, Iterable


CONCEPT_RECORD_ID = "19241151"
ZENODO_API = "https://zenodo.org/api/records/{record_id}"
MARKER_NAME = ".linkd_data_release.json"

EXPECTED_ARCHIVES = (
    "Database.zip",
    "EHR_Results.zip",
    "DrugResponse.zip",
    "Target_Disease_Association.zip",
    "DrugTargetMetrics_csvs.zip",
    "DrugTargetMetrics_parquet_part1.zip",
    "DrugTargetMetrics_parquet_part2.zip",
    "DrugTargetMetrics_parquet_part3.zip",
    "DrugTargetMetrics_parquet_part4.zip",
    "DrugTargetMetrics_parquet_part5.zip",
    "DrugTargetMetrics_parquet_part6.zip",
    "DrugTargetMetrics_parquet_part7.zip",
    "DrugTargetMetrics_parquet_part8.zip",
    "DrugTargetMetrics_parquet_part9.zip",
    "DrugTargetMetrics_parquet_part10.zip",
)

REQUIRED_FILES = {
    "Database": (
        "onco_genes.csv",
        "protein_info.csv",
    ),
    "EHR_Results": (
        "uk_biobank_drug_disease.csv",
        "mount_sinai_drug_disease.csv",
    ),
    "DrugResponse": ("drug_response_crispr_correlation.csv",),
    "Target_Disease_Association": (
        "disease_target_overall.csv",
        "disease_target_by_source.csv",
        "causal_gene_disease.csv",
        "drug_target_disease.csv",
        "target_priority.csv",
    ),
    "DrugTargetMetrics": (
        "drug_selectivity_metrics.csv",
        "target_binding_stats.csv",
        "target_centric_pan/drug_index.json",
        "target_centric_pan/target_index.json",
    ),
}


class DownloadError(RuntimeError):
    """Raised when a remote release cannot be installed safely."""


def _request_json(url: str) -> dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"Accept": "application/json", "User-Agent": "LinkD-data-downloader/1"},
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            return json.load(response)
    except (urllib.error.URLError, json.JSONDecodeError) as exc:
        raise DownloadError(f"Could not read Zenodo metadata: {exc}") from exc


def resolve_release(record_id: str) -> dict[str, Any]:
    """Resolve a concept or version record and validate its file inventory."""
    metadata = _request_json(ZENODO_API.format(record_id=record_id))
    files = {item["key"]: item for item in metadata.get("files", [])}
    missing = sorted(set(EXPECTED_ARCHIVES) - set(files))
    if missing:
        raise DownloadError(
            "Zenodo release is missing required application archives: "
            + ", ".join(missing)
        )
    return {
        "record_id": str(metadata["id"]),
        "doi": str(metadata.get("doi", "")),
        "files": {name: files[name] for name in EXPECTED_ARCHIVES},
    }


def _checksum_parts(value: str) -> tuple[str, str]:
    try:
        algorithm, expected = value.lower().split(":", 1)
    except ValueError as exc:
        raise DownloadError(f"Unsupported Zenodo checksum value: {value!r}") from exc
    if algorithm not in hashlib.algorithms_available:
        raise DownloadError(f"Unsupported checksum algorithm: {algorithm}")
    return algorithm, expected


def _download(item: dict[str, Any], destination: Path) -> None:
    """Stream one archive to a .part file and verify its Zenodo checksum."""
    algorithm, expected = _checksum_parts(str(item["checksum"]))
    digest = hashlib.new(algorithm)
    request = urllib.request.Request(
        item["links"]["self"],
        headers={"User-Agent": "LinkD-data-downloader/1"},
    )
    part = destination.with_suffix(destination.suffix + ".part")
    part.unlink(missing_ok=True)
    try:
        with urllib.request.urlopen(request, timeout=120) as response, part.open("wb") as out:
            total = int(response.headers.get("Content-Length", 0))
            received = 0
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
                digest.update(chunk)
                received += len(chunk)
                if total:
                    percent = min(100, received * 100 // total)
                    sys.stdout.write(
                        f"\r  {destination.name}: "
                        f"{received / 2**20:.1f}/{total / 2**20:.1f} MiB ({percent}%)"
                    )
                    sys.stdout.flush()
        if total:
            print()
        if digest.hexdigest().lower() != expected:
            raise DownloadError(
                f"Checksum mismatch for {destination.name}: expected "
                f"{algorithm}:{expected}, got {algorithm}:{digest.hexdigest()}"
            )
        part.replace(destination)
    except BaseException:
        part.unlink(missing_ok=True)
        raise


def _safe_members(archive: zipfile.ZipFile) -> Iterable[zipfile.ZipInfo]:
    """Yield ZIP members after rejecting traversal, duplicates, and links."""
    seen: set[str] = set()
    for member in archive.infolist():
        normalized = member.filename.replace("\\", "/")
        path = PurePosixPath(normalized)
        if (
            not normalized
            or "\x00" in normalized
            or path.is_absolute()
            or ".." in path.parts
        ):
            raise DownloadError(f"Unsafe path in {archive.filename}: {member.filename!r}")
        key = str(path).rstrip("/")
        if key in seen:
            raise DownloadError(f"Duplicate path in {archive.filename}: {member.filename!r}")
        seen.add(key)
        unix_mode = member.external_attr >> 16
        if stat.S_ISLNK(unix_mode):
            raise DownloadError(f"Symbolic link in {archive.filename}: {member.filename!r}")
        yield member


def _extract(
    archive_path: Path,
    staging_root: Path,
    installed_paths: set[str] | None = None,
) -> None:
    with zipfile.ZipFile(archive_path) as archive:
        for member in _safe_members(archive):
            relative = PurePosixPath(member.filename.replace("\\", "/"))
            if not relative.parts or relative.parts[0] not in REQUIRED_FILES:
                raise DownloadError(
                    f"Unexpected top-level path in {archive_path.name}: "
                    f"{member.filename!r}"
                )
            destination = staging_root.joinpath(*relative.parts)
            if member.is_dir():
                destination.mkdir(parents=True, exist_ok=True)
                continue
            key = relative.as_posix()
            if installed_paths is not None and key in installed_paths:
                raise DownloadError(
                    f"Duplicate file across application archives: {key!r}"
                )
            if installed_paths is not None:
                installed_paths.add(key)
            destination.parent.mkdir(parents=True, exist_ok=True)
            with archive.open(member) as source, destination.open("wb") as target:
                shutil.copyfileobj(source, target, length=1024 * 1024)


def validate_installation(data_root: Path) -> list[str]:
    """Return human-readable validation errors for an installed release."""
    errors: list[str] = []
    for directory, required in REQUIRED_FILES.items():
        for relative in required:
            path = data_root / directory / relative
            if not path.is_file() or path.stat().st_size == 0:
                errors.append(f"missing or empty: {directory}/{relative}")

    chunks = sorted(
        (data_root / "DrugTargetMetrics" / "target_centric_pan").glob(
            "target_centric_pan_uniprot_chunk_*.parquet"
        )
    )
    if len(chunks) != 100:
        errors.append(
            "DrugTargetMetrics/target_centric_pan must contain 100 parquet chunks "
            f"(found {len(chunks)})"
        )

    for directory, required in REQUIRED_FILES.items():
        for relative in required:
            if not relative.endswith(".csv"):
                continue
            path = data_root / directory / relative
            if not path.is_file() or path.stat().st_size == 0:
                continue
            try:
                with path.open("r", encoding="utf-8-sig") as handle:
                    header = handle.readline().strip()
                if not header or "," not in header:
                    errors.append(f"invalid CSV header: {directory}/{relative}")
            except OSError as exc:
                errors.append(f"unreadable: {directory}/{relative} ({exc})")
    return errors


def _marker_for(release: dict[str, Any]) -> dict[str, Any]:
    return {
        "concept_doi": "10.5281/zenodo.19241151",
        "record_id": release["record_id"],
        "version_doi": release["doi"],
        "archives": {
            name: release["files"][name]["checksum"] for name in EXPECTED_ARCHIVES
        },
    }


def _read_marker(data_root: Path) -> dict[str, Any] | None:
    try:
        return json.loads((data_root / MARKER_NAME).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return None


def verify_current(data_root: Path, release: dict[str, Any]) -> list[str]:
    errors = validate_installation(data_root)
    expected = _marker_for(release)
    marker = _read_marker(data_root)
    if marker != expected:
        errors.append(
            f"{MARKER_NAME} is absent, invalid, or does not match Zenodo record "
            f"{release['record_id']}"
        )
    return errors


def _atomic_install(staging_root: Path, data_root: Path) -> None:
    """Replace the five validated dataset directories, with rollback on failure."""
    backup_root = staging_root.parent / f"{staging_root.name}-backup"
    backup_root.mkdir()
    installed: list[str] = []
    moved_old: list[str] = []
    try:
        for directory in REQUIRED_FILES:
            source = staging_root / directory
            target = data_root / directory
            backup = backup_root / directory
            if target.exists():
                target.replace(backup)
                moved_old.append(directory)
            source.replace(target)
            installed.append(directory)
    except BaseException:
        for directory in reversed(installed):
            target = data_root / directory
            if target.exists():
                shutil.rmtree(target)
        for directory in reversed(moved_old):
            backup = backup_root / directory
            if backup.exists():
                backup.replace(data_root / directory)
        raise
    finally:
        if backup_root.exists():
            shutil.rmtree(backup_root)


def install_release(data_root: Path, release: dict[str, Any]) -> None:
    data_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(
        prefix=".linkd-download-", dir=data_root
    ) as temporary:
        work = Path(temporary)
        staging = work / "staging"
        downloads = work / "downloads"
        staging.mkdir()
        downloads.mkdir()
        installed_paths: set[str] = set()

        for name in EXPECTED_ARCHIVES:
            print(f"Downloading {name}")
            archive = downloads / name
            _download(release["files"][name], archive)
            print(f"  extracting {name}")
            _extract(archive, staging, installed_paths)
            archive.unlink()

        errors = validate_installation(staging)
        if errors:
            raise DownloadError(
                "Downloaded release failed validation:\n  - " + "\n  - ".join(errors)
            )

        _atomic_install(staging, data_root)
        marker = _marker_for(release)
        marker_path = data_root / MARKER_NAME
        marker_tmp = marker_path.with_suffix(".tmp")
        marker_tmp.write_text(
            json.dumps(marker, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        marker_tmp.replace(marker_path)


def _default_destination() -> Path:
    configured = Path(os.getenv("DATABASE_DIR", "data"))
    return configured.parent if configured.name == "Database" else configured


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Install LinkD application data from the latest version of "
            "https://doi.org/10.5281/zenodo.19241151"
        )
    )
    parser.add_argument(
        "--record-id",
        default=CONCEPT_RECORD_ID,
        help="Zenodo concept or version record ID (default: %(default)s)",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=_default_destination(),
        help="Data root containing Database/, DrugTargetMetrics/, and related folders",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Download and replace a valid current installation",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Verify the installed data and release marker without downloading",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    data_root = args.destination.expanduser().resolve()
    try:
        release = resolve_release(str(args.record_id))
        print(
            f"Resolved Zenodo record {release['record_id']} "
            f"({release['doi'] or 'DOI unavailable'})"
        )
        errors = verify_current(data_root, release)
        if args.verify_only:
            if errors:
                raise DownloadError(
                    f"Installation at {data_root} is not verified:\n  - "
                    + "\n  - ".join(errors)
                )
            print(f"Verified LinkD application data at {data_root}")
            return 0

        if not args.force and not errors:
            print(f"Verified current LinkD application data at {data_root}; nothing to do.")
            return 0

        install_release(data_root, release)
        final_errors = verify_current(data_root, release)
        if final_errors:
            raise DownloadError(
                "Installation completed but final verification failed:\n  - "
                + "\n  - ".join(final_errors)
            )
        print(f"Installed and verified LinkD application data at {data_root}")
        return 0
    except (DownloadError, OSError, zipfile.BadZipFile) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
