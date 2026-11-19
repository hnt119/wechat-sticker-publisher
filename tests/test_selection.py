"""Keep selected and unfinished albums independent in a multi-album project."""
from __future__ import annotations

import io
import json
import shutil
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from zipfile import ZipFile

from wechat_sticker_publisher.cli import main


class AlbumSelectionTests(unittest.TestCase):
    def setUp(self):
        scratch = tempfile.TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.project = Path(scratch.name).resolve() / "creator"
        sample = Path(__file__).resolve().parents[1] / "examples" / "sample-album"
        shutil.copytree(sample, self.project, ignore=shutil.ignore_patterns("releases", "__pycache__"))
        self.config = self.project / "publishing-config"
        self.sample = self.config / "chestnut.json"

    def add_draft(self, album_id: str) -> None:
        (self.config / f"{album_id}.json").write_text(
            json.dumps({"id": album_id, "type": "animated", "sticker_directory": "incoming"}),
            encoding="utf-8",
        )

    def build(self, *flags: str, expected_code: int) -> dict:
        stdout = io.StringIO()
        with redirect_stdout(stdout):
            code = main(["--project", str(self.project), "build", "--offline", "--json", *flags])
        self.assertEqual(code, expected_code, stdout.getvalue())
        return json.loads(stdout.getvalue())

    def test_selected_album_ignores_unrelated_malformed_and_unfinished_manifests(self):
        (self.config / "broken.yml").write_text("id: [unfinished\n", encoding="utf-8")
        self.add_draft("future")
        report = self.build("--pack", "chestnut", expected_code=0)
        self.assertEqual([(r["album"], r["status"]) for r in report["albums"]],
                         [("chestnut", "TECHNICAL_PASS")])
        self.assertEqual(len(list(Path(report["release"]).glob("*.zip"))), 1)

    def test_absent_discovery_directory_produces_partial_album_with_briefs(self):
        self.add_draft("future")
        report = self.build("--all", expected_code=1)
        results = {r["album"]: r for r in report["albums"]}
        self.assertEqual(results["chestnut"]["status"], "TECHNICAL_PASS")
        draft = results["future"]
        self.assertEqual(draft["status"], "INCOMPLETE")
        self.assertEqual(draft["stickers"], 0)
        briefs = {brief["role"]: brief for brief in draft["briefs"]}
        self.assertEqual(briefs["additional-stickers"]["number_needed"], 8)
        self.assertEqual(len(briefs), 6)
        self.assertEqual(len(list(Path(report["release"]).glob("*.zip"))), 2)
        self.assertFalse((self.project / "incoming").exists())

    def test_draft_ids_cannot_collide_with_a_named_album_or_previews(self):
        config = json.loads(self.sample.read_text(encoding="utf-8"))
        config["name"] = "Spring"
        self.sample.write_text(json.dumps(config), encoding="utf-8")
        self.add_draft("chestnut-Spring")
        self.add_draft("previews")
        report = self.build("--all", expected_code=1)
        release = Path(report["release"])
        by_id = {}
        for archive in release.glob("*.zip"):
            with ZipFile(archive) as bundle:
                metadata = json.loads(bundle.read("metadata.json"))
                by_id[metadata["id"]] = metadata
                self.assertFalse(any("previews" in name for name in bundle.namelist()))
        self.assertEqual(set(by_id), {"chestnut", "chestnut-Spring", "previews"})
        self.assertEqual(len(by_id["chestnut"]["stickers"]), 8)
        self.assertEqual(by_id["chestnut-Spring"]["stickers"], [])
        self.assertEqual(by_id["previews"]["stickers"], [])
        self.assertFalse((release / "previews/metadata.json").exists())
