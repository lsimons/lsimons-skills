"""Tests for `scripts.references`."""

from pathlib import Path

from scripts.manifest import SkillEntry
from scripts.references import group_by_skill, scan_references

RENAMED = SkillEntry("https://example.com/repo", "tdd", "mp-tdd")
UNCHANGED = SkillEntry("https://example.com/repo", "kept", "kept")


def make_skill(skills_dir: Path, name: str, text: str, filename: str = "SKILL.md") -> Path:
    path = skills_dir / name / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_finds_a_reference_to_a_renamed_skill(tmp_path: Path) -> None:
    make_skill(tmp_path, "other", "see the tdd skill\n")

    found = scan_references([RENAMED], tmp_path)

    assert [(r.lineno, r.upstream_name, r.local_names) for r in found] == [(1, "tdd", ("mp-tdd",))]
    assert not found[0].ambiguous
    assert found[0].line == "see the tdd skill"


def test_ignores_skills_that_were_not_renamed(tmp_path: Path) -> None:
    make_skill(tmp_path, "other", "see the kept skill\n")
    assert scan_references([UNCHANGED], tmp_path) == []


def test_does_not_match_the_already_renamed_name(tmp_path: Path) -> None:
    """`mp-tdd` contains `tdd`, but is not a stale reference."""
    make_skill(tmp_path, "other", "see mp-tdd\n")
    assert scan_references([RENAMED], tmp_path) == []


def test_does_not_match_inside_longer_words(tmp_path: Path) -> None:
    make_skill(tmp_path, "other", "tddx and xtdd and tdd-plus and plus-tdd\n")
    assert scan_references([RENAMED], tmp_path) == []


def test_scans_a_skills_own_directory(tmp_path: Path) -> None:
    """Upstream refers to its own skills by name, and those need renaming too."""
    make_skill(tmp_path, "mp-tdd", "this tdd skill\n")
    assert len(scan_references([RENAMED], tmp_path)) == 1


def test_scans_nested_markdown_but_not_other_files(tmp_path: Path) -> None:
    make_skill(tmp_path, "other", "tdd\n", filename="references/deep.md")
    make_skill(tmp_path, "other", "tdd\n", filename="scripts/run.sh")

    found = scan_references([RENAMED], tmp_path)

    assert [r.path.name for r in found] == ["deep.md"]


def test_reports_each_matching_line_once_per_name(tmp_path: Path) -> None:
    make_skill(tmp_path, "other", "tdd and tdd on one line\nplain\ntdd again\n")
    assert [r.lineno for r in scan_references([RENAMED], tmp_path)] == [1, 3]


def test_group_by_skill_orders_by_reference_count(tmp_path: Path) -> None:
    other = SkillEntry("https://example.com/repo", "teach", "mp-teach")
    make_skill(tmp_path, "a", "tdd\ntdd\nteach\n")

    grouped = group_by_skill(scan_references([RENAMED, other], tmp_path))

    assert list(grouped) == ["tdd", "teach"]
    assert len(grouped["tdd"]) == 2


def test_reports_every_candidate_when_two_packs_share_a_name(tmp_path: Path) -> None:
    """osmani and superpowers both ship `test-driven-development`; neither wins."""
    both = [
        SkillEntry("https://example.com/a", "shared", "ao-shared"),
        SkillEntry("https://example.com/b", "shared", "s-shared"),
    ]
    make_skill(tmp_path, "other", "see shared\n")

    found = scan_references(both, tmp_path)

    assert len(found) == 1
    assert found[0].local_names == ("ao-shared", "s-shared")
    assert found[0].ambiguous
