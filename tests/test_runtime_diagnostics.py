"""First-run diagnostics for healthy and incomplete offline installations."""
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
from PIL import __version__ as pillow_version
from yaml import __version__ as yaml_version

from wechat_sticker_publisher import __version__
from wechat_sticker_publisher.cli import main


def test_doctor_identifies_active_runtime(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv("USERPROFILE", str(tmp_path))
    monkeypatch.chdir(tmp_path)
    assert main(["skill", "doctor", "--agent", "codex", "--json"]) == 0
    runtime = json.loads(capsys.readouterr().out)["runtime"]
    assert runtime["publisher"] == __version__
    assert runtime["executable"] == sys.executable
    assert runtime["Pillow"] == pillow_version and runtime["PyYAML"] == yaml_version


@pytest.mark.parametrize(("module", "dependency"), [("PIL", "Pillow"), ("yaml", "PyYAML")])
def test_missing_dependency_explains_repair(tmp_path, module, dependency):
    # Python finds the temporary broken module first; the installed CLI runs normally.
    (tmp_path / (module + ".py")).write_text(
        f"raise ModuleNotFoundError('Missing {module}', name={module!r})", encoding="utf-8"
    )
    src = Path(__file__).resolve().parents[1] / "src"
    proc = subprocess.run(
        [sys.executable, "-m", "wechat_sticker_publisher.cli", "skill", "doctor"],
        cwd=tmp_path, env={**os.environ, "PYTHONPATH": str(src)}, capture_output=True, text=True,
    )
    assert proc.returncode == 2
    assert f"Missing {dependency}" in proc.stderr and "wheelhouse" in proc.stderr
    assert "Traceback" not in proc.stderr
