"""Exercise skill management in temporary projects and homes, without a model or network."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess

import pytest

from wechat_sticker_publisher import skills
from wechat_sticker_publisher.cli import main

NAME = skills.NAME
REPO = Path(__file__).resolve().parents[1]
NATIVE = [
    ("codex", ".agents", ".agents"),
    ("claude-code", ".claude", ".claude"),
    ("gemini-cli", ".gemini", ".gemini"),
    ("cursor", ".cursor", ".cursor"),
    ("opencode", ".opencode", ".config/opencode"),
    ("github-copilot", ".github", ".copilot"),
    ("dsh", ".dsh", ".dsh"),
]


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    project, home = tmp_path / "creator", tmp_path / "home"
    project.mkdir()
    home.mkdir()
    for key in ("DSH_HOME", "DSH_AGENTS_HOME", "CLAUDE_CONFIG_DIR", "XDG_CONFIG_HOME",
                "DEEPSEEK_API_KEY", "DSH_API_KEY", "OPENAI_API_KEY"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.setenv("USERPROFILE", str(home))
    monkeypatch.chdir(project)
    monkeypatch.setenv("PATH", str(tmp_path / "no-executables"))

    def offline(*args, **kwargs):
        pytest.fail("Installer and standalone sample workflow must stay offline")
    monkeypatch.setattr(socket, "getaddrinfo", offline)
    monkeypatch.setattr(socket.socket, "connect", offline)
    return project, home


def command(action, *extra, agent="dsh", scope="project"):
    return main(["skill", action, "--agent", agent, "--scope", scope, *extra])


@pytest.mark.parametrize(("agent", "project_dir", "user_dir"), NATIVE)
@pytest.mark.parametrize("scope", ["project", "user"])
def test_adapter_native_lifecycle(workspace, capsys, agent, project_dir, user_dir, scope):
    project, home = workspace
    dest = ((project / project_dir) if scope == "project" else (home / user_dir)) / "skills" / NAME
    assert command("install", "--dry-run", agent=agent, scope=scope) == 0
    assert list(project.iterdir()) == list(home.iterdir()) == []
    assert command("install", agent=agent, scope=scope) == 0
    for name, content in skills.skill_files().items():
        assert (dest / name).read_bytes() == content
    before = (dest / "SKILL.md").stat().st_mtime_ns
    assert command("install", agent=agent, scope=scope) == 0
    assert (dest / "SKILL.md").stat().st_mtime_ns == before
    assert command("uninstall", "--dry-run", agent=agent, scope=scope) == 0
    assert (dest / "SKILL.md").is_file()
    assert command("uninstall", agent=agent, scope=scope) == 0
    assert not dest.exists()
    assert command("uninstall", agent=agent, scope=scope) == 0


@pytest.mark.parametrize("scope", ["project", "user"])
def test_dsh_reuses_shared_skill_without_duplicate(workspace, scope):
    project, home = workspace
    base = project if scope == "project" else home
    assert command("install", "--layout", "shared", scope=scope) == 0
    bundle = base / ".agents" / "skills" / NAME
    assert bundle.is_dir()
    assert command("install", scope=scope) == 0
    assert not (base / ".dsh").exists()
    assert command("uninstall", scope=scope) == 0
    assert not bundle.exists()


def test_canonical_copy_is_discoverable_but_never_claimed(workspace):
    project, _ = workspace
    bundle = project / ".agents" / "skills" / NAME
    shutil.copytree(REPO / ".agents" / "skills" / NAME, bundle)
    assert command("install") == 0
    assert not (project / ".dsh").exists()
    assert command("uninstall") == 2
    assert not (bundle / skills.RECEIPT).exists()
    assert (bundle / "SKILL.md").is_file()
    assert command("install", scope="user") == 0  # Explicit user scope works inside the toolkit.


def test_shared_ownership_between_harnesses(workspace):
    project, _ = workspace
    assert command("install", agent="codex") == 0
    assert command("install", agent="dsh") == 0
    assert command("uninstall", agent="dsh") == 2
    assert (project / ".agents" / "skills" / NAME).is_dir()


def test_dsh_overrides_and_git_worktree_root(workspace, monkeypatch, tmp_path):
    project, home = workspace
    monkeypatch.setenv("DSH_HOME", str(tmp_path / "custom-dsh"))
    monkeypatch.setenv("DSH_AGENTS_HOME", "~/shared-skills")
    sub = project / "album"
    sub.mkdir()
    (project / ".git").write_text("gitdir: example")
    monkeypatch.chdir(sub)
    assert command("install") == 0
    assert (project / ".dsh" / "skills" / NAME).is_dir()
    assert not (sub / ".dsh").exists()
    assert command("install", scope="user") == 0
    assert (tmp_path / "custom-dsh" / "skills" / NAME).is_dir()
    assert command("uninstall", scope="user") == 0
    assert command("install", "--layout", "shared", scope="user") == 0
    assert (home / "shared-skills" / "skills" / NAME).is_dir()


def test_dsh_relative_or_blank_home(workspace, monkeypatch):
    project, home = workspace
    monkeypatch.setenv("DSH_HOME", "relative-config")
    monkeypatch.setenv("DSH_AGENTS_HOME", "  ")
    assert command("install", scope="user") == 0
    assert (project / "relative-config" / "skills" / NAME).is_dir()
    assert command("uninstall", scope="user") == 0
    assert command("install", "--layout", "shared", scope="user") == 0
    assert (home / ".agents" / "skills" / NAME).is_dir()


def test_dsh_ranked_duplicate_diagnostics(workspace, capsys):
    project, home = workspace
    for base in [project / ".dsh", project / ".agents", home / ".dsh", home / ".agents"]:
        bundle = base / "skills" / NAME
        shutil.copytree(REPO / ".agents" / "skills" / NAME, bundle)
    assert main(["skill", "doctor", "--agent", "dsh", "--json"]) == 0
    row = json.loads(capsys.readouterr().out)["agents"][0]
    assert row["first_standard_candidate"] == str(project / ".dsh" / "skills" / NAME)
    assert row["candidates"] == [
        str(base / d / "skills" / NAME)
        for base, d in [(project, ".dsh"), (project, ".agents"), (home, ".dsh"), (home, ".agents")]
    ]
    assert command("install") == 2
    assert command("uninstall") == 2
    assert all(Path(path).is_dir() for path in row["candidates"])


@pytest.mark.parametrize("filename", ["other/SKILL.md", "different.md", NAME + ".md"])
def test_dsh_respects_named_and_flat_collisions(workspace, filename):
    project, _ = workspace
    existing = project / ".agents" / "skills" / filename
    existing.parent.mkdir(parents=True)
    content = f"---\nname: {NAME}\ndescription: Existing local customization\n---\nCustom"
    existing.write_text(content)
    assert command("install") == 2
    assert not (project / ".dsh").exists()
    assert existing.read_text() == content


@pytest.mark.parametrize("change", ["content", "added", "empty-dir", "symlink", "receipt"])
def test_uninstall_preserves_modifications(workspace, tmp_path, change):
    project, _ = workspace
    assert command("install") == 0
    path = project / ".dsh" / "skills" / NAME
    if change == "content":
        (path / "SKILL.md").write_text("creator edits")
    elif change == "added":
        (path / "notes.md").write_text("creator notes")
    elif change == "empty-dir":
        (path / "custom").mkdir()
    elif change == "symlink":
        (path / "references/publishing-workflow.md").unlink()
        (path / "references/publishing-workflow.md").symlink_to(tmp_path / "missing")
    else:
        (path / skills.RECEIPT).write_text("{}")
    assert command("uninstall") == 2
    assert path.is_dir()
    assert (path / "SKILL.md").is_file()


@pytest.mark.parametrize("level", [".dsh", ".dsh/skills", f".dsh/skills/{NAME}"])
def test_install_refuses_symlink_paths(workspace, tmp_path, level):
    project, _ = workspace
    outside = tmp_path / "foreign"
    outside.mkdir()
    link = project / level
    link.parent.mkdir(parents=True, exist_ok=True)
    link.symlink_to(outside, target_is_directory=True)
    assert command("install") == 2
    assert link.is_symlink()
    assert not list(outside.iterdir())


def test_failed_install_leaves_no_partial_skill(workspace, monkeypatch):
    project, _ = workspace
    def fail_write(self, data):
        raise OSError("disk full")
    monkeypatch.setattr(Path, "write_bytes", fail_write)
    assert command("install") == 2
    assert list((project / ".dsh" / "skills").iterdir()) == []


def test_dsh_doctor_detection_without_credentials(workspace, monkeypatch, tmp_path, capsys):
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    monkeypatch.setenv("PATH", str(fake_bin))
    filename = "dsh.exe" if os.name == "nt" else "dsh"
    for expected in (None, str(fake_bin / filename)):
        if expected:
            Path(expected).write_text("#!/bin/sh\nexit 1\n")
            Path(expected).chmod(0o755)
        assert main(["skill", "doctor", "--agent", "dsh", "--json"]) == 0
        report = json.loads(capsys.readouterr().out)
        assert report["agents"][0]["runtime"] == expected
        assert report["agents"][0]["candidates"] == []
        assert set(report["skill_resources"]) == set(skills.FILES)


def test_resources_survive_packaged_import_without_checkout(workspace, monkeypatch, tmp_path):
    package = tmp_path / "package"
    bundle = package / "skill_data"
    shutil.copytree(REPO / ".agents" / "skills" / NAME, bundle)
    monkeypatch.setattr(skills.resources, "files", lambda _: package)
    monkeypatch.setattr(skills, "__file__", str(package / "skills.py"))
    assert skills.skill_files() == {name: (bundle / name).read_bytes() for name in skills.FILES}
    assert command("install") == 0


def test_unconfigured_dsh_allows_direct_offline_fallback(workspace, capsys):
    project, _ = workspace
    shutil.copytree(REPO / "examples/sample-album", project, dirs_exist_ok=True,
                    ignore=shutil.ignore_patterns("releases", "__pycache__"))
    assert command("install") == 0
    assert main(["validate", "--json"]) == 0
    assert main(["build", "--offline", "--release", "sample"]) == 0
    assert list((project / "releases").rglob("*.zip"))


def test_native_and_shared_operations_use_one_lock(workspace):
    project, _ = workspace
    with skills._lock(project):
        assert command("install", "--layout", "shared") == 2
    assert not (project / ".agents").exists()
    assert command("install") == 0


def test_dsh_coincident_override_is_one_candidate(workspace, monkeypatch, capsys):
    _, home = workspace
    monkeypatch.setenv("DSH_HOME", str(home / "both"))
    monkeypatch.setenv("DSH_AGENTS_HOME", str(home / "both"))
    assert command("install", "--layout", "shared", scope="user") == 0
    assert command("install", scope="user") == 0
    capsys.readouterr()
    assert main(["skill", "doctor", "--agent", "dsh", "--json"]) == 0
    assert len(json.loads(capsys.readouterr().out)["agents"][0]["candidates"]) == 1
    assert command("uninstall", scope="user") == 0


def test_extra_files_do_not_qualify_for_reuse(workspace):
    project, _ = workspace
    assert command("install") == 0
    extra = project / ".dsh" / "skills" / NAME / "creator.md"
    extra.write_text("keep")
    assert command("install") == command("uninstall") == 2
    assert extra.read_text() == "keep"


@pytest.mark.parametrize(("agent", "directory", "_"), NATIVE)
def test_declared_name_collides_across_adapters(workspace, agent, directory, _):
    project, _home = workspace
    bundle = project / directory / "skills" / "local-version"
    bundle.mkdir(parents=True)
    (bundle / "SKILL.md").write_text(f"---\nname: {NAME}\ndescription: Custom version\n---\n")
    assert command("install", agent=agent) == 2
    assert (bundle / "SKILL.md").is_file()
    assert not (bundle.parent / NAME).exists()


def test_linked_dsh_skill_with_alias_is_a_read_only_candidate(workspace, tmp_path, capsys):
    project, _ = workspace
    actual = tmp_path / "existing-skill"
    shutil.copytree(REPO / ".agents" / "skills" / NAME, actual)
    link = project / ".dsh" / "skills" / "linked-alias"
    link.parent.mkdir(parents=True)
    link.symlink_to(actual, target_is_directory=True)
    assert main(["skill", "doctor", "--agent", "dsh", "--json"]) == 0
    row = json.loads(capsys.readouterr().out)["agents"][0]
    assert row["first_standard_candidate"] == str(link)
    assert command("install") == command("uninstall") == 2
    assert link.is_symlink()
    assert (actual / "SKILL.md").is_file()

@pytest.mark.skipif(os.name != "nt", reason="NTFS directory junction")
def test_windows_install_refuses_junction(workspace, tmp_path):
    project, _ = workspace
    outside = tmp_path / "outside"
    outside.mkdir()
    junction = project / ".dsh"
    subprocess.run([os.environ["COMSPEC"], "/d", "/c", "mklink", "/J", str(junction), str(outside)],
                   check=True, capture_output=True)
    assert junction.is_dir()
    assert command("install") == 2
    assert not list(outside.iterdir())
