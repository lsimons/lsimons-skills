"""Tests for `scripts.manifest`."""

from pathlib import Path

import pytest

from scripts.manifest import SkillEntry, load_manifest
from scripts.paths import SKILLS_DIR, UPSTREAM_MANIFEST


def write_manifest(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "upstream-skills.txt"
    path.write_text(content)
    return path


def test_parses_entries_in_file_order(tmp_path: Path) -> None:
    path = write_manifest(
        tmp_path,
        "https://example.com/a first\nhttps://example.com/b second\n",
    )
    assert load_manifest(path) == [
        SkillEntry("https://example.com/a", "first"),
        SkillEntry("https://example.com/b", "second"),
    ]


def test_ignores_blank_lines_and_comments(tmp_path: Path) -> None:
    path = write_manifest(
        tmp_path,
        "# header\n\n   \n  https://example.com/a only  \n# trailing\n",
    )
    assert load_manifest(path) == [SkillEntry("https://example.com/a", "only")]


def test_empty_manifest_yields_no_entries(tmp_path: Path) -> None:
    assert load_manifest(write_manifest(tmp_path, "# nothing here\n")) == []


@pytest.mark.parametrize("line", ["https://example.com/a", "a b c"])
def test_rejects_lines_without_exactly_two_fields(tmp_path: Path, line: str) -> None:
    path = write_manifest(tmp_path, f"{line}\n")
    with pytest.raises(ValueError, match=r"upstream-skills\.txt:1"):
        load_manifest(path)


def test_real_manifest_is_parseable_and_fully_vendored() -> None:
    """Every declared skill must be committed under skills/."""
    entries = load_manifest(UPSTREAM_MANIFEST)
    assert entries, "expected at least one declared skill"
    missing = [e.name for e in entries if not (SKILLS_DIR / e.name).is_dir()]
    assert missing == []


def test_real_manifest_has_no_duplicate_skill_names() -> None:
    names = [entry.name for entry in load_manifest(UPSTREAM_MANIFEST)]
    assert len(names) == len(set(names))
