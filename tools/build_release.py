"""Build the current Git commit twice and collect matching release distributions."""
import argparse
import gzip
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import tempfile
import tomllib


def normalize_sdist(archive: Path, epoch: int) -> None:
    """Remove local ownership and wall-clock time from setuptools tar/gzip headers."""
    normalized = archive.with_suffix(".normalized")
    with tarfile.open(archive) as original, normalized.open("wb") as output:
        with gzip.GzipFile(filename="", fileobj=output, mode="wb", compresslevel=9, mtime=epoch) as gzip_file:
            with tarfile.open(fileobj=gzip_file, mode="w", format=tarfile.PAX_FORMAT) as target:
                for entry in sorted(original, key=lambda member: member.name):
                    if not (entry.isdir() or entry.isfile()):
                        raise ValueError(f"Unexpected archive member: {entry.name}")
                    entry.uid = entry.gid = 0
                    entry.uname = entry.gname = ""
                    entry.mtime = epoch
                    entry.pax_headers = {}
                    target.addfile(entry, original.extractfile(entry) if entry.isfile() else None)
    normalized.replace(archive)


def build(snapshot: Path, directory: Path, epoch: int) -> dict[str, str]:
    source = directory / "source"
    output = directory / "dist"
    with tarfile.open(snapshot) as archive:
        archive.extractall(source, filter="data")
    with (source / "pyproject.toml").open("rb") as config:
        version = tomllib.load(config)["project"]["version"]
    subprocess.run(
        [sys.executable, "-m", "build", "--no-isolation", "--outdir", str(output), str(source)],
        env={**os.environ, "SOURCE_DATE_EPOCH": str(epoch)}, check=True,
    )
    prefix = f"wechat_sticker_publisher-{version}"
    sdist = output / f"{prefix}.tar.gz"
    wheel = output / f"{prefix}-py3-none-any.whl"
    if set(output.iterdir()) != {sdist, wheel}:
        raise ValueError("Expected one source archive and one universal wheel")
    normalize_sdist(sdist, epoch)
    return {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in (wheel, sdist)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="new or empty destination directory")
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        parser.error("destination already contains files")
    repo = Path(__file__).resolve().parents[1]
    commit, timestamp = subprocess.check_output(
        ["git", "show", "-s", "--format=%H %ct", "HEAD"], cwd=repo, text=True,
    ).split()
    with tempfile.TemporaryDirectory() as scratch:
        root = Path(scratch)
        snapshot = root / "source.tar"
        subprocess.run(["git", "archive", "-o", snapshot, commit], cwd=repo, check=True)
        first = build(snapshot, root / "first", int(timestamp))
        second = build(snapshot, root / "second", int(timestamp))
        if first != second:
            raise ValueError(f"Independent builds disagree: {first} versus {second}")
        output.mkdir(parents=True, exist_ok=True)
        for name in first:
            shutil.copyfile(root / "first" / "dist" / name, output / name)
        checksums = "".join(f"{first[name]}  {name}\n" for name in sorted(first))
        (output / "SHA256SUMS").write_text(checksums, encoding="ascii", newline="\n")
        print(f"Verified two builds of {commit}\n{checksums}", end="")


if __name__ == "__main__":
    main()
