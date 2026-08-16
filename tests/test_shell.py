"""Tests for `scripts.shell`."""

import subprocess
from pathlib import Path
from typing import Any

import pytest

from scripts import shell


class FakeRun:
    """Stands in for `subprocess.run`, recording calls and returning a fixed status."""

    def __init__(self, returncode: int = 0) -> None:
        self.returncode = returncode
        self.calls: list[tuple[list[str], dict[str, Any]]] = []

    def __call__(self, cmd: list[str], **kwargs: Any) -> subprocess.CompletedProcess[str]:
        self.calls.append((cmd, kwargs))
        return subprocess.CompletedProcess(cmd, self.returncode)


def stub_command_exists(monkeypatch: pytest.MonkeyPatch, *, present: bool) -> None:
    """Force `shell.command_exists` to report every command as present/absent."""

    def fake(cmd: str) -> bool:
        return present

    monkeypatch.setattr(shell, "command_exists", fake)


def test_command_exists_true_for_a_real_command() -> None:
    assert shell.command_exists("python3")


def test_command_exists_false_for_a_missing_command() -> None:
    assert not shell.command_exists("definitely-not-a-real-command-xyz")


def test_run_executes_and_returns_status(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeRun(returncode=3)
    monkeypatch.setattr(subprocess, "run", fake)

    assert shell.run(["echo", "hi"], cwd=Path("/tmp")) == 3
    assert fake.calls == [(["echo", "hi"], {"check": False, "cwd": Path("/tmp")})]


def test_run_skips_execution_in_dry_run(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    fake = FakeRun(returncode=1)
    monkeypatch.setattr(subprocess, "run", fake)

    assert shell.run(["rm", "-rf", "/"], dry_run=True) == 0
    assert fake.calls == []
    assert "[DRY-RUN] would run: rm -rf /" in capsys.readouterr().out


def test_npm_install_global_skips_execution_in_dry_run(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    fake = FakeRun()
    monkeypatch.setattr(subprocess, "run", fake)

    assert shell.npm_install_global("skills", dry_run=True)
    assert fake.calls == []


def test_npm_install_global_fails_without_npm(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stub_command_exists(monkeypatch, present=False)

    assert not shell.npm_install_global("skills")
    assert "npm not found" in capsys.readouterr().err


def test_npm_install_global_invokes_npm(monkeypatch: pytest.MonkeyPatch) -> None:
    fake = FakeRun()
    monkeypatch.setattr(subprocess, "run", fake)
    stub_command_exists(monkeypatch, present=True)

    assert shell.npm_install_global("skills@1.2.3")
    assert fake.calls[0][0] == ["npm", "install", "-g", "--ignore-scripts", "skills@1.2.3"]


def test_npm_install_global_reports_failure(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(subprocess, "run", FakeRun(returncode=1))
    stub_command_exists(monkeypatch, present=True)

    assert not shell.npm_install_global("skills")
