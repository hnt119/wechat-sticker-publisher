"""Snapshot allocation and all-or-nothing release publication."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
from unittest.mock import patch

import pytest

from wechat_sticker_publisher.metadata import albums
from wechat_sticker_publisher.packaging import build, commit_release


def test_concurrent_publishers_reserve_distinct_directories(tmp_path):
    label = "test"
    sources = []
    for i in range(8):
        source = tmp_path / f"work-{i}"
        source.mkdir()
        (source / "marker").write_text(str(i))
        sources.append(source)

    with ThreadPoolExecutor(max_workers=8) as pool:
        paths = list(pool.map(lambda p: commit_release(p, tmp_path, label), sources))

    assert len(set(paths)) == 8
    assert [(p / "marker").read_text() for p in paths] == list(map(str, range(8)))
    assert len(list(tmp_path.iterdir())) == 8


def test_failed_packaging_preserves_prior_release(tmp_path):
    sample = Path(__file__).resolve().parents[1] / "examples/sample-album"
    project = tmp_path / "project"
    shutil.copytree(sample, project, ignore=shutil.ignore_patterns("releases"))
    selected = albums(project, None)
    first, _ = build(project, selected, "first", False, None)
    first_archive = next(first.glob("*.zip"))
    original_zip = first_archive.read_bytes()
    with patch("wechat_sticker_publisher.packaging.finish_album", side_effect=OSError("storage full")):
        with pytest.raises(OSError, match="storage full"):
            build(project, selected, "first", False, None)
    assert first_archive.read_bytes() == original_zip
    assert list(first.parent.iterdir()) == [first]
