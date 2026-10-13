"""`rag setup`: download QASPER v0.3 dev and test, verify, extract.

Downloads the official S3 tarballs into data/qasper/ (git-ignored),
verifies size and sha256 before extracting, extracts only the split
jsons the experiment reads, and is idempotent: an already-present,
verified tarball with its extracted json is left untouched. No dataset
text is ever written outside data/.
"""

from __future__ import annotations

import hashlib
import tarfile
import urllib.request
from dataclasses import dataclass
from pathlib import Path

QASPER_BASE_URL = "https://qasper-dataset.s3.us-west-2.amazonaws.com"


@dataclass(frozen=True)
class Tarball:
    filename: str
    sha256: str
    size: int
    members: tuple[str, ...]

    @property
    def url(self) -> str:
        return f"{QASPER_BASE_URL}/{self.filename}"


QASPER_TARBALLS: tuple[Tarball, ...] = (
    Tarball(
        filename="qasper-train-dev-v0.3.tgz",
        sha256="a28fdf966db827bcee3d873107d6b6669864fb7ca8fbf73a192f5e39191bdb5a",
        size=10_835_856,
        members=("qasper-dev-v0.3.json",),
    ),
    Tarball(
        filename="qasper-test-and-evaluator-v0.3.tgz",
        sha256="72a52a41193e2838b8074f80ac074b94f956b84886c36a61c58a7df4171bdd72",
        size=3_865_061,
        members=("qasper-test-v0.3.json",),
    ),
)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def split_file_path(data_dir: Path, split: str) -> Path:
    return data_dir / "qasper" / f"qasper-{split}-v0.3.json"


def ensure_split_files(data_dir: Path, splits: tuple[str, ...]) -> dict[str, Path]:
    """Return {split: path}; raise with a hint when a split is missing."""
    paths = {}
    missing = []
    for split in splits:
        path = split_file_path(data_dir, split)
        if path.is_file():
            paths[split] = path
        else:
            missing.append(split)
    if missing:
        raise FileNotFoundError(
            f"missing QASPER split file(s) {sorted(missing)} under {data_dir / 'qasper'}; run `uv run rag setup` first"
        )
    return paths


def download_tarball(tarball: Tarball, dest: Path) -> None:
    """Stream the tarball to dest, then verify size and sha256."""
    tmp = dest.with_suffix(dest.suffix + ".part")
    with urllib.request.urlopen(tarball.url) as response, tmp.open("wb") as out:
        while True:
            block = response.read(1024 * 1024)
            if not block:
                break
            out.write(block)
    size = tmp.stat().st_size
    if size != tarball.size:
        tmp.unlink(missing_ok=True)
        raise ValueError(f"{tarball.filename}: expected {tarball.size} bytes, downloaded {size}")
    digest = _sha256_file(tmp)
    if digest != tarball.sha256:
        tmp.unlink(missing_ok=True)
        raise ValueError(f"{tarball.filename}: sha256 mismatch (got {digest})")
    tmp.replace(dest)


def verify_tarball(tarball: Tarball, dest: Path) -> bool:
    """True when dest exists with the pinned size and sha256."""
    if not dest.is_file():
        return False
    if dest.stat().st_size != tarball.size:
        raise ValueError(
            f"{dest.name}: size {dest.stat().st_size} != pinned {tarball.size}; delete the file and re-run setup"
        )
    digest = _sha256_file(dest)
    if digest != tarball.sha256:
        raise ValueError(f"{dest.name}: sha256 mismatch (got {digest}); delete the file and re-run setup")
    return True


def extract_members(tarball: Tarball, archive: Path, out_dir: Path) -> list[str]:
    """Extract only the split jsons; refuse anything outside the pinned set."""
    extracted: list[str] = []
    with tarfile.open(archive, "r:gz") as tf:
        for member in tf.getmembers():
            name = Path(member.name).name
            if name not in tarball.members:
                continue
            if not member.isfile():
                continue
            source = tf.extractfile(member)
            if source is None:
                continue
            target = out_dir / name
            target.write_bytes(source.read())
            extracted.append(name)
    missing = [m for m in tarball.members if m not in extracted]
    if missing:
        raise ValueError(f"{archive.name}: missing expected member(s) {missing}")
    return extracted


def setup(data_dir: Path, tarballs: tuple[Tarball, ...] = QASPER_TARBALLS) -> list[str]:
    """Make the QASPER split jsons present and verified. Returns report lines."""
    qasper_dir = data_dir / "qasper"
    qasper_dir.mkdir(parents=True, exist_ok=True)
    lines: list[str] = []
    for tarball in tarballs:
        archive = qasper_dir / tarball.filename
        if verify_tarball(tarball, archive):
            lines.append(f"verified {tarball.filename} (sha256 ok)")
        else:
            download_tarball(tarball, archive)
            lines.append(f"downloaded {tarball.filename} ({tarball.size:,} bytes, sha256 ok)")
        if all((qasper_dir / member).is_file() for member in tarball.members):
            lines.append(f"present {', '.join(tarball.members)}")
        else:
            extracted = extract_members(tarball, archive, qasper_dir)
            lines.append(f"extracted {', '.join(extracted)}")
    return lines
