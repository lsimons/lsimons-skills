"""Tests for `scripts.console`."""

import pytest

from scripts import console


def test_info_success_warn_dry_go_to_stdout(capsys: pytest.CaptureFixture[str]) -> None:
    console.info("a")
    console.success("b")
    console.warn("c")
    console.dry("d")
    captured = capsys.readouterr()
    assert captured.out == "[INFO] a\n[SUCCESS] b\n[WARN] c\n[DRY-RUN] d\n"
    assert captured.err == ""


def test_error_goes_to_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    console.error("boom")
    captured = capsys.readouterr()
    assert captured.out == ""
    assert captured.err == "[ERROR] boom\n"
