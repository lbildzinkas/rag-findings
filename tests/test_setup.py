"""`rag setup`: checksum verification, extraction, idempotence.

The download path is exercised through file:// URLs, so no test touches
the network; the pinned QASPER tarballs are verified end-to-end by the
real local `rag setup` run.
"""

from __future__ import annotations

import hashlib
import io
import tarfile
from pathlib import Path

import pytest

from rag.setup_cmd import (
    Tarball,
    download_tarball,
    ensure_split_files,
    extract_members,
    setup,
    verify_tarball,
)


def make_tgz(members: dict[str, str]) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz") as tf:
        for name, content in members.items():
            info = tarfile.TarInfo(name)
            payload = content.encode("utf-8")
            info.size = len(payload)
            tf.addfile(info, io.BytesIO(payload))
    return buffer.getvalue()


def make_tarball(tmp_path: Path, members: dict[str, str], prefix: str = "fixture") -> tuple[Tarball, Path]:
    data = make_tgz(members)
    dest = tmp_path / f"{prefix}.tgz"
    dest.write_bytes(data)
    tarball = Tarball(
        filename=dest.name,
        sha256=hashlib.sha256(data).hexdigest(),
        size=len(data),
        members=tuple(members),
    )
    return tarball, dest


def test_setup_downloads_extracts_and_is_idempotent(tmp_path):
    members = {"qasper-dev-v0.3.json": '{"p": {}}'}
    data = make_tgz(members)
    source = tmp_path / "source.tgz"
    source.write_bytes(data)
    data_dir = tmp_path / "data"

    class LocalTarball(Tarball):
        @property
        def url(self):
            return source.as_uri()

    local = LocalTarball(
        filename="fixture.tgz",
        sha256=hashlib.sha256(data).hexdigest(),
        size=len(data),
        members=tuple(members),
    )
    first = setup(data_dir, (local,))
    assert any("downloaded" in line for line in first)
    assert (data_dir / "qasper" / "qasper-dev-v0.3.json").is_file()

    second = setup(data_dir, (local,))
    assert any("verified" in line for line in second)
    assert any("present" in line for line in second)
    # idempotent: no re-download, no re-extraction churn
    assert first != second


def test_verify_tarball_detects_tampering(tmp_path):
    members = {"qasper-dev-v0.3.json": "x"}
    tarball, dest = make_tarball(tmp_path, members)
    assert verify_tarball(tarball, dest)
    dest.write_bytes(dest.read_bytes() + b"tampered")
    with pytest.raises(ValueError, match="sha256 mismatch|size"):
        verify_tarball(tarball, dest)


def test_download_tarball_rejects_bad_checksum(tmp_path):
    members = {"qasper-dev-v0.3.json": "x"}
    source = tmp_path / "source.tgz"
    source.write_bytes(make_tgz(members))

    class LocalTarball(Tarball):
        @property
        def url(self):
            return source.as_uri()

    tarball = LocalTarball(
        filename="fixture.tgz",
        sha256="0" * 64,  # wrong on purpose
        size=source.stat().st_size,
        members=tuple(members),
    )
    with pytest.raises(ValueError, match="sha256 mismatch"):
        download_tarball(tarball, tmp_path / "fixture.tgz")
    assert not (tmp_path / "fixture.tgz").exists()


def test_download_tarball_rejects_wrong_size(tmp_path):
    members = {"qasper-dev-v0.3.json": "x"}
    source = tmp_path / "source.tgz"
    source.write_bytes(make_tgz(members))

    class LocalTarball(Tarball):
        @property
        def url(self):
            return source.as_uri()

    tarball = LocalTarball(
        filename="fixture.tgz",
        sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
        size=source.stat().st_size + 1,
        members=tuple(members),
    )
    with pytest.raises(ValueError, match="expected .* bytes"):
        download_tarball(tarball, tmp_path / "fixture.tgz")


def test_extract_members_skips_unpinned_files(tmp_path):
    members = {"qasper-dev-v0.3.json": "keep", "README.md": "skip me", "evil/../../x": "nope"}
    tarball, dest = make_tarball(tmp_path, members, prefix="mixed")
    out_dir = tmp_path / "out"
    out_dir.mkdir()
    pinned = Tarball(
        filename=tarball.filename,
        sha256=tarball.sha256,
        size=tarball.size,
        members=("qasper-dev-v0.3.json",),
    )
    extracted = extract_members(pinned, dest, out_dir)
    assert extracted == ["qasper-dev-v0.3.json"]
    assert sorted(p.name for p in out_dir.iterdir()) == ["qasper-dev-v0.3.json"]


def test_extract_members_requires_pinned_member(tmp_path):
    buffer = make_tgz({"other.json": "x"})
    dest = tmp_path / "only.tgz"
    dest.write_bytes(buffer)
    pinned = Tarball(
        filename=dest.name,
        sha256=hashlib.sha256(buffer).hexdigest(),
        size=len(buffer),
        members=("qasper-dev-v0.3.json",),
    )
    with pytest.raises(ValueError, match="missing expected member"):
        extract_members(pinned, dest, tmp_path)


def test_ensure_split_files_missing_hint(tmp_path):
    with pytest.raises(FileNotFoundError, match="rag setup"):
        ensure_split_files(tmp_path, ("dev",))
