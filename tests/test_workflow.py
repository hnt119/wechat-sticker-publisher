"""Exercise the CLI on copies of the public example without remote services."""

import hashlib
import io
import json
import shutil
import socket
import tempfile
import unittest
from contextlib import ExitStack, redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import Mock, patch
from zipfile import ZipFile

import yaml
from PIL import Image

from wechat_sticker_publisher.cli import main
from wechat_sticker_publisher.metadata import albums


EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "sample-album"


def tree_digest(directory):
    return {
        path.relative_to(directory).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(directory.rglob("*")) if path.is_file()
    }


class OfflineWorkflowTests(unittest.TestCase):
    def setUp(self):
        work = tempfile.TemporaryDirectory()
        self.addCleanup(work.cleanup)
        self.root = Path(work.name).resolve() / "project"
        shutil.copytree(EXAMPLE, self.root, ignore=shutil.ignore_patterns("releases", "__pycache__"))
        self.manifest = next((self.root / "publishing-config").glob("*.json"))
        self.config = json.loads(self.manifest.read_text(encoding="utf-8"))
        self.album_id = self.config["id"]
        self.release_root = self.root / "releases" / "wechat"

        self.network_attempts = []
        stack = ExitStack()
        self.addCleanup(stack.close)
        for method in ("getaddrinfo", "create_connection"):
            stack.enter_context(patch.object(socket, method, self.reject_network))
        for method in ("connect", "connect_ex", "sendto"):
            stack.enter_context(patch.object(socket.socket, method, self.reject_network))
        self.addCleanup(self.assertEqual, self.network_attempts, [])

    def reject_network(self, *args, **kwargs):
        self.network_attempts.append("network attempted")
        raise AssertionError("The offline workflow attempted a network operation")

    def save_config(self):
        self.manifest.write_text(json.dumps(self.config, ensure_ascii=False), encoding="utf-8")

    def run_cli(self, *arguments, expect=0, project=None):
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            status = main(["--project", str(project or self.root), *arguments])
        self.assertEqual(status, expect, f"CLI {arguments} returned {status}: {output.getvalue()} {errors.getvalue()}")
        return output.getvalue() + errors.getvalue()

    def album_dir(self, label):
        album = self.release_root / label / f"{self.album_id}-{self.config['name']}"
        self.assertTrue(album.is_dir(), f"missing release {album}")
        return album

    def test_offline_sample_validates_and_builds_only_listed_assets(self):
        source_digests = tree_digest(self.root / "stickers")
        # Unlisted synthetic files exercise the same isolation boundary as a
        # real creator's reference masters, project documents and secrets.
        private_marker = b"synthetic-private-sentinel-02671"
        (self.root / ".env").write_bytes(private_marker)
        (self.root / "stickers" / "unlisted-note.md").write_bytes(private_marker)
        shutil.copyfile(self.root / self.config["stickers"][0]["path"], self.root / "unlisted-master.png")
        with patch("wechat_sticker_publisher.artwork.entry_points") as discovery:
            inventory = self.run_cli("inventory", "--all", "--json")
            json.loads(inventory)
            self.assertIn(self.album_id, inventory)
            self.run_cli("validate", "--all")
            self.run_cli("build", "--all", "--offline", "--release", "smoke")
            discovery.assert_not_called()
        album = self.album_dir("smoke")
        self.assertEqual(len(list((album / "stickers").iterdir())), 8)
        self.assertEqual(len(list((album / "supplementary").iterdir())), 5)
        self.assertEqual(source_digests, {key: value for key, value in tree_digest(self.root / "stickers").items()
                                         if key != "unlisted-note.md"})
        for name in ("metadata.json", "上架文案.md", "submission-checklist.md", "validation-report.md"):
            self.assertTrue((album / name).is_file(), name)
        copy = (album / "上架文案.md").read_text(encoding="utf-8")
        for field in ("name", "description", "appreciation"):
            self.assertIn(self.config[field], copy)
        self.assertIn("TECHNICAL_PASS", (album / "validation-report.md").read_text(encoding="utf-8"))
        release = album.parent
        self.assertTrue((release / "release-summary.md").is_file())
        for group in ("stickers", "supplementary"):
            with Image.open(release / "previews" / f"{self.album_id}-{group}.png") as sheet:
                sheet.verify()
        (archive,) = release.glob("*.zip")
        with ZipFile(archive) as bundle:
            self.assertIsNone(bundle.testzip())
            archived = {name for name in bundle.namelist() if not name.endswith("/")}
            extracted = {file.relative_to(album).as_posix() for file in album.rglob("*") if file.is_file()}
            if all(name.startswith(album.name + "/") for name in archived):
                archived = {name.split("/", 1)[1] for name in archived}
            self.assertEqual(archived, extracted)
            for file in bundle.infolist():
                self.assertFalse(Path(file.filename).is_absolute())
                self.assertNotIn("..", Path(file.filename).parts)
                self.assertNotIn(private_marker, bundle.read(file))
                self.assertNotIn(str(self.root).encode(), bundle.read(file))
        self.assertFalse(any("unlisted" in p.name or p.name == ".env" for p in release.rglob("*")))

    def test_missing_artwork_yields_dimensions_path_and_repairable_partial_release(self):
        source = self.root / self.config["supplementary"]["cover"]
        original = source.read_bytes()
        source.unlink()
        with patch("wechat_sticker_publisher.artwork.entry_points") as discovery:
            self.run_cli("validate", "--pack", self.album_id, expect=1)
            missing = json.loads(self.run_cli("assets", "missing", "--all", "--json", expect=1))
            self.assertEqual([row["role"] for row in missing[self.album_id]], ["cover"])
            briefs = json.loads(self.run_cli("assets", "briefs", "--all", "--json", expect=1))
            self.run_cli("build", "--offline", "--release", "partial", expect=1)
            discovery.assert_not_called()
        partial = self.album_dir("partial")
        self.assertFalse(any((partial / "supplementary").glob("cover.*")))
        self.assertEqual(len(list((partial / "stickers").iterdir())), 8)
        self.assertIn("INCOMPLETE", (partial / "validation-report.md").read_text(encoding="utf-8"))
        (brief,) = json.loads((partial / "artwork-briefs.json").read_text(encoding="utf-8"))
        self.assertEqual([brief], briefs[self.album_id])
        self.assertEqual(brief["size_px"], [240, 240])
        self.assertEqual(brief["supply_at"], self.config["supplementary"]["cover"])
        self.assertIn("PNG", brief["formats"])
        before = tree_digest(partial.parent)
        source.write_bytes(original)
        self.run_cli("build", "--offline", "--release", "repaired")
        self.assertEqual(before, tree_digest(partial.parent))
        self.assertTrue(any((self.album_dir("repaired") / "supplementary").glob("cover.*")))

    def test_optional_provider_unavailable_preserves_prior_release_and_offline_work(self):
        self.run_cli("build", "--release", "original")
        original = tree_digest(self.release_root / "original")
        (self.root / self.config["supplementary"]["icon"]).unlink()
        self.run_cli("build", "--generate-missing", "--release", "partial", expect=1)
        album = self.album_dir("partial")
        self.assertEqual(len(list((album / "stickers").iterdir())), 8)
        self.assertEqual(len(list((album / "supplementary").iterdir())), 4)
        self.assertIn("provider", (album / "validation-report.md").read_text(encoding="utf-8").lower())
        self.assertEqual(original, tree_digest(self.release_root / "original"))

    def test_opted_in_provider_receives_only_missing_role_and_named_references(self):
        role = "icon"
        source = self.root / self.config["supplementary"][role]
        icon = source.read_bytes()
        source.unlink()
        ref = self.config["stickers"][0]["path"]
        self.config["references"] = [ref]
        self.save_config()
        calls = []

        class LocalTestProvider:
            def generate(self, brief, references, destination):
                calls.append((brief, references))
                destination.write_bytes(icon)

        entry = Mock()
        entry.load.return_value = LocalTestProvider
        with patch("wechat_sticker_publisher.artwork.entry_points", return_value=[entry]) as discover:
            self.run_cli("build", "--generate-missing", "--provider", "test",
                         "--release", "assisted")
        discover.assert_called_once_with(group="wechat_sticker_publisher.artwork", name="test")
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0][0]["role"], role)
        self.assertEqual(calls[0][1], [self.root / ref])
        self.assertFalse(source.exists())
        album = self.album_dir("assisted")
        self.assertEqual((album / "supplementary" / "icon.png").read_bytes(), icon)
        self.assertIn("GENERATE", (album / "validation-report.md").read_text(encoding="utf-8"))

    def test_repeated_build_is_reproducible_and_retains_previous_release(self):
        self.run_cli("build", "--release", "test-1")
        digests = tree_digest(self.release_root / "test-1")
        self.run_cli("build", "--release", "test-1")
        folders = [p for p in self.release_root.iterdir() if p.is_dir() and p.name != "test-1"]
        self.assertEqual(len(folders), 1)
        self.assertEqual(digests, tree_digest(self.release_root / "test-1"))
        (first,) = (self.release_root / "test-1").glob("*.zip")
        (second,) = folders[0].glob("*.zip")
        self.assertEqual(first.read_bytes(), second.read_bytes())

    def test_copy_limits_count_limits_and_required_fields(self):
        # Exercise both inclusive ends of every documented interval independently.
        original = self.config["stickers"][0]
        for count in (7, 8, 24, 25):
            self.config["stickers"] = [dict(original, id=f"pose-{index}") for index in range(count)]
            self.save_config()
            with self.subTest(count=count):
                errors = albums(self.root, self.album_id)[0].issues()
                self.assertEqual(bool(errors), count not in (8, 24), errors)
        self.config["stickers"] = self.config["stickers"][:8]
        for field, low, high in (("name", 1, 8), ("description", 1, 80), ("appreciation", 5, 15)):
            previous = self.config[field]
            for length in (low - 1, low, high, high + 1):
                self.config[field] = "春" * length
                self.save_config()
                with self.subTest(field=field, length=length):
                    errors = albums(self.root, self.album_id)[0].issues()
                    self.assertEqual(bool(errors), not low <= length <= high, errors)
            self.config[field] = previous
        for name in ("春 日", "春！"):
            self.config["name"] = name
            self.save_config()
            self.assertTrue(albums(self.root, self.album_id)[0].issues())
        self.config["name"] = "春日"
        self.config["characters"] = []
        self.config["status"] = ""
        self.save_config()
        self.assertGreaterEqual(len(albums(self.root, self.album_id)[0].issues()), 2)

    def test_duplicate_id_and_visually_identical_art_are_reported(self):
        rows = self.config["stickers"]
        rows[1]["id"] = rows[0]["id"]
        self.save_config()
        self.assertIn("duplicate sticker id",
                      self.run_cli("validate", "--json", expect=1).lower())
        rows[1]["id"] = "new-id"
        self.save_config()
        with Image.open(self.root / rows[0]["path"]) as artwork:
            artwork.save(self.root / rows[1]["path"], compress_level=1)
        self.assertIn("duplicate rendered sticker",
                      self.run_cli("validate", "--json", expect=1).lower())

    def test_paths_cannot_escape_the_creator_project(self):
        external = self.root.parent / "private.png"
        shutil.copyfile(self.root / self.config["stickers"][0]["path"], external)
        for target in ("../private.png", str(external)):
            self.config["stickers"][0]["path"] = target
            self.save_config()
            self.run_cli("build", "--release", "rejected", expect=2)
            self.assertFalse((self.release_root / "rejected").exists())
        link = self.root / "outside.png"
        try:
            link.symlink_to(external)
        except OSError as exc:
            self.skipTest(f"Symlinks unavailable on this filesystem: {exc}")
        self.config["stickers"][0]["path"] = link.name
        self.save_config()
        self.run_cli("build", "--release", "rejected", expect=2)
        self.assertFalse((self.release_root / "rejected").exists())

    def test_yaml_manifest_and_directory_based_init(self):
        self.manifest.with_suffix(".yaml").write_text(yaml.safe_dump(self.config), encoding="utf-8")
        self.manifest.unlink()
        self.run_cli("validate", "--all")
        new_project = self.root.parent / "from-scratch"
        new_project.mkdir()
        self.run_cli("init", "--pack", "fresh", project=new_project)
        config_path = new_project / "publishing-config" / "fresh.json"
        starter = json.loads(config_path.read_text(encoding="utf-8"))
        self.run_cli("init", "--pack", "fresh", project=new_project, expect=2)
        for field in ("name", "description", "appreciation", "characters"):
            starter[field] = self.config[field]
        config_path.write_text(json.dumps(starter, ensure_ascii=False), encoding="utf-8")
        shutil.copytree(self.root / "stickers", new_project / starter["sticker_directory"], dirs_exist_ok=True)
        shutil.copytree(self.root / "supplementary", new_project / starter["supplementary_directory"], dirs_exist_ok=True)
        self.run_cli("inventory", project=new_project)
        self.run_cli("validate", project=new_project)
        self.run_cli("build", project=new_project)
