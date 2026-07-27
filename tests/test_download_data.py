"""Security and release-marker tests for the Zenodo application downloader."""

from __future__ import annotations

import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts import download_data


def _zip_bytes(files: dict[str, bytes]) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, payload in files.items():
            archive.writestr(name, payload)
    return buffer.getvalue()


def test_safe_extraction_rejects_traversal(tmp_path: Path) -> None:
    archive_path = tmp_path / "unsafe.zip"
    archive_path.write_bytes(_zip_bytes({"../outside.txt": b"not allowed"}))
    with pytest.raises(download_data.DownloadError, match="Unsafe path"):
        download_data._extract(archive_path, tmp_path / "staging")
    assert not (tmp_path / "outside.txt").exists()


def test_safe_extraction_rejects_unexpected_root(tmp_path: Path) -> None:
    archive_path = tmp_path / "unexpected.zip"
    archive_path.write_bytes(_zip_bytes({"unrelated/file.txt": b"not allowed"}))
    with pytest.raises(download_data.DownloadError, match="Unexpected top-level"):
        download_data._extract(archive_path, tmp_path / "staging")


def test_safe_extraction_rejects_cross_archive_duplicates(tmp_path: Path) -> None:
    first = tmp_path / "first.zip"
    second = tmp_path / "second.zip"
    member = "Database/onco_genes.csv"
    first.write_bytes(_zip_bytes({member: b"a,b\n1,2\n"}))
    second.write_bytes(_zip_bytes({member: b"a,b\n3,4\n"}))
    installed: set[str] = set()
    download_data._extract(first, tmp_path / "staging", installed)
    with pytest.raises(download_data.DownloadError, match="Duplicate file"):
        download_data._extract(second, tmp_path / "staging", installed)


def test_download_removes_partial_file_on_checksum_mismatch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    payload = b"complete response"

    class Response(io.BytesIO):
        headers = {"Content-Length": str(len(payload))}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.close()

    monkeypatch.setattr(
        download_data.urllib.request,
        "urlopen",
        lambda request, timeout: Response(payload),
    )
    destination = tmp_path / "archive.zip"
    item = {
        "checksum": "md5:" + hashlib.md5(b"different").hexdigest(),
        "links": {"self": "https://example.invalid/archive.zip"},
    }
    with pytest.raises(download_data.DownloadError, match="Checksum mismatch"):
        download_data._download(item, destination)
    assert not destination.exists()
    assert not destination.with_suffix(".zip.part").exists()


def test_interrupted_download_leaves_no_partial_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Interrupted:
        headers = {}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

        def read(self, size: int) -> bytes:
            del size
            raise OSError("connection interrupted")

    monkeypatch.setattr(
        download_data.urllib.request,
        "urlopen",
        lambda request, timeout: Interrupted(),
    )
    destination = tmp_path / "archive.zip"
    item = {
        "checksum": "md5:" + hashlib.md5(b"").hexdigest(),
        "links": {"self": "https://example.invalid/archive.zip"},
    }
    with pytest.raises(OSError, match="interrupted"):
        download_data._download(item, destination)
    assert not destination.exists()
    assert not destination.with_suffix(".zip.part").exists()


def test_release_marker_detects_new_version(tmp_path: Path) -> None:
    release_one = {
        "record_id": "1",
        "doi": "10.5281/zenodo.1",
        "files": {
            name: {"checksum": f"md5:{index:032x}"}
            for index, name in enumerate(download_data.EXPECTED_ARCHIVES)
        },
    }
    release_two = {
        **release_one,
        "record_id": "2",
        "doi": "10.5281/zenodo.2",
    }
    (tmp_path / download_data.MARKER_NAME).write_text(
        json.dumps(download_data._marker_for(release_one)), encoding="utf-8"
    )
    errors = download_data.verify_current(tmp_path, release_two)
    assert any(download_data.MARKER_NAME in error for error in errors)


def test_resolve_release_requires_all_application_archives(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(
        download_data,
        "_request_json",
        lambda url: {
            "id": 1,
            "doi": "10.5281/zenodo.1",
            "files": [{"key": "Database.zip", "checksum": "md5:0", "links": {}}],
        },
    )
    with pytest.raises(download_data.DownloadError, match="missing required"):
        download_data.resolve_release(download_data.CONCEPT_RECORD_ID)
