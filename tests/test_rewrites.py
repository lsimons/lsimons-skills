"""Tests for `scripts.rewrites`."""

from pathlib import Path

import pytest

from scripts.paths import REWRITES_FILE
from scripts.rewrites import apply_rewrites, load_rewrites

RULES = """
["ao-using-agent-skills"]
"SKILL.md" = [["-> interview-me", "-> ao-interview-me"]]
"""


def write_rules(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "skill-rewrites.toml"
    path.write_text(content)
    return path


def make_skill(tmp_path: Path, text: str) -> Path:
    skill_dir = tmp_path / "ao-using-agent-skills"
    skill_dir.mkdir()
    (skill_dir / "SKILL.md").write_text(text)
    return skill_dir


def test_missing_file_means_no_rules(tmp_path: Path) -> None:
    assert load_rewrites(tmp_path / "absent.toml") == {}


def test_loads_pairs_per_skill_and_file(tmp_path: Path) -> None:
    assert load_rewrites(write_rules(tmp_path, RULES)) == {
        "ao-using-agent-skills": {"SKILL.md": [("-> interview-me", "-> ao-interview-me")]}
    }


@pytest.mark.parametrize(
    ("content", "match"),
    [
        ('["skill"]\n"SKILL.md" = "nope"\n', "expected a list"),
        ('["skill"]\n"SKILL.md" = [["only"]]\n', "pairs of strings"),
        ('["skill"]\n"SKILL.md" = [[1, 2]]\n', "pairs of strings"),
        ('["skill"]\n"SKILL.md" = [["", "new"]]\n', "must not be empty"),
        ('["skill"]\nSKILL = 1\n', "expected a list"),
    ],
)
def test_rejects_malformed_rules(tmp_path: Path, content: str, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        load_rewrites(write_rules(tmp_path, content))


def test_rejects_a_skill_that_is_not_a_table(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="expected a table"):
        load_rewrites(write_rules(tmp_path, 'skill = "nope"\n'))


def test_applies_every_occurrence_and_reports_the_count(tmp_path: Path) -> None:
    skill_dir = make_skill(tmp_path, "-> interview-me here\nand -> interview-me again\n")
    rules = load_rewrites(write_rules(tmp_path, RULES))

    result = apply_rewrites("ao-using-agent-skills", skill_dir, rules)

    assert result.replacements == 2
    assert result.stale == []
    assert (skill_dir / "SKILL.md").read_text() == (
        "-> ao-interview-me here\nand -> ao-interview-me again\n"
    )


def test_reports_a_rule_whose_text_is_absent_as_stale(tmp_path: Path) -> None:
    """Upstream changed the wording; the rule needs re-authoring, not ignoring."""
    skill_dir = make_skill(tmp_path, "upstream rewrote this line\n")
    rules = load_rewrites(write_rules(tmp_path, RULES))

    result = apply_rewrites("ao-using-agent-skills", skill_dir, rules)

    assert result.applied == []
    assert [r.old for r in result.stale] == ["-> interview-me"]
    assert "interview-me" in result.stale[0].describe()


def test_reports_a_rule_for_a_missing_file_as_stale(tmp_path: Path) -> None:
    skill_dir = tmp_path / "ao-using-agent-skills"
    skill_dir.mkdir()
    rules = load_rewrites(write_rules(tmp_path, RULES))

    result = apply_rewrites("ao-using-agent-skills", skill_dir, rules)

    assert len(result.stale) == 1


def test_a_skill_without_rules_is_left_alone(tmp_path: Path) -> None:
    skill_dir = make_skill(tmp_path, "untouched\n")
    result = apply_rewrites("other-skill", skill_dir, load_rewrites(write_rules(tmp_path, RULES)))

    assert result == ([], [], 0)
    assert (skill_dir / "SKILL.md").read_text() == "untouched\n"


def test_real_ruleset_is_parseable() -> None:
    assert isinstance(load_rewrites(REWRITES_FILE), dict)
