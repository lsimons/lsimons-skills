"""Tests for `scripts.placeholders`."""

from pathlib import Path

import pytest

from scripts import placeholders
from scripts.placeholders import (
    extract_tokens,
    load_ignores,
    main,
    render_body,
    stale_ignores,
    sync_blocks,
)

BLOCK = """<!-- placeholders: assets/README-template.md -->
```
<old>
```
<!-- /placeholders -->
"""


@pytest.fixture
def skills(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """A `skills/` tree the module's path constants point at."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    (tmp_path / "disabled").mkdir()
    ignore_file = tmp_path / "placeholder-tokens.toml"
    _ = ignore_file.write_text("[ignore]\n")
    monkeypatch.setattr(placeholders, "SKILLS_DIR", skills_dir)
    monkeypatch.setattr(placeholders, "DISABLED_DIR", tmp_path / "disabled")
    monkeypatch.setattr(placeholders, "PLACEHOLDER_IGNORE_FILE", ignore_file)
    return skills_dir


def make_skill(skills_dir: Path, name: str, template: str, prose: str = BLOCK) -> Path:
    asset = skills_dir / name / "assets" / "README-template.md"
    asset.parent.mkdir(parents=True)
    _ = asset.write_text(template)
    skill = skills_dir / name / "SKILL.md"
    _ = skill.write_text(prose)
    return skill


def test_extracts_tokens_deduplicated_and_sorted(skills: Path) -> None:
    make_skill(skills, "s", "<b> text <a> more <b>\n")
    assert extract_tokens(skills / "s/assets/README-template.md", {}) == ["<a>", "<b>"]


def test_ignores_declared_tokens(skills: Path) -> None:
    make_skill(skills, "s", "<a> <keep>\n")
    ignores = {"s/assets/README-template.md": ("<keep>",)}
    assert extract_tokens(skills / "s/assets/README-template.md", ignores) == ["<a>"]


def test_does_not_match_across_lines_or_nested(skills: Path) -> None:
    make_skill(skills, "s", "<open\nclose> and <<nested>>\n")
    assert extract_tokens(skills / "s/assets/README-template.md", {}) == ["<nested>"]


def test_renders_a_flat_list_for_a_file_target(skills: Path) -> None:
    make_skill(skills, "s", "<a>\n<b>\n")
    assert render_body(skills / "s", "assets/README-template.md", {}) == "```\n<a>\n<b>\n```\n"


def test_renders_a_grouped_list_for_a_directory_target(skills: Path) -> None:
    make_skill(skills, "s", "<a>\n")
    _ = (skills / "s/assets/empty.md").write_text("no tokens\n")
    body = render_body(skills / "s", "assets/", {})
    assert body == "```\nassets/README-template.md\n  <a>\n```\n"


def test_skips_non_template_suffixes_in_a_directory_target(skills: Path) -> None:
    make_skill(skills, "s", "<a>\n")
    _ = (skills / "s/assets/logo.svg").write_text("<svg>\n")
    body = render_body(skills / "s", "assets/", {})
    assert body == "```\nassets/README-template.md\n  <a>\n```\n"


def test_rejects_a_target_that_does_not_exist(skills: Path) -> None:
    make_skill(skills, "s", "<a>\n")
    with pytest.raises(ValueError, match="no such template"):
        _ = render_body(skills / "s", "assets/missing.md", {})


def test_check_reports_drift_without_writing(skills: Path) -> None:
    skill = make_skill(skills, "s", "<new>\n")

    drifted = sync_blocks(apply=False)

    assert [(d.path, d.target) for d in drifted] == [(skill, "assets/README-template.md")]
    assert skill.read_text() == BLOCK


def test_apply_rewrites_the_block(skills: Path) -> None:
    skill = make_skill(skills, "s", "<new>\n")

    assert len(sync_blocks(apply=True)) == 1

    assert "<new>" in skill.read_text()
    assert "<old>" not in skill.read_text()
    assert sync_blocks(apply=False) == []


def test_leaves_files_without_a_block_alone(skills: Path) -> None:
    make_skill(skills, "s", "<old>\n", prose="no markers here\n")
    assert sync_blocks(apply=False) == []


def test_stale_ignores_flags_a_missing_template(skills: Path) -> None:
    make_skill(skills, "s", "<a>\n")
    assert stale_ignores({"s/assets/gone.md": ("<a>",)}) == ["s/assets/gone.md: no such template"]


def test_stale_ignores_flags_a_token_that_no_longer_appears(skills: Path) -> None:
    make_skill(skills, "s", "<a>\n")
    stale = stale_ignores({"s/assets/README-template.md": ("<a>", "<gone>")})
    assert stale == ["s/assets/README-template.md: <gone>"]


def test_stale_ignores_accepts_a_disabled_skill(skills: Path) -> None:
    disabled = skills.parent / "disabled"
    asset = disabled / "s" / "assets" / "README-template.md"
    asset.parent.mkdir(parents=True)
    _ = asset.write_text("<a>\n")
    assert stale_ignores({"s/assets/README-template.md": ("<a>",)}) == []


def test_main_fails_on_drift_and_passes_after_apply(skills: Path) -> None:
    make_skill(skills, "s", "<new>\n")

    assert main([]) == 1
    assert main(["--apply"]) == 0
    assert main([]) == 0


def test_main_fails_on_a_stale_ignore_even_with_apply(skills: Path) -> None:
    make_skill(skills, "s", "<new>\n")
    _ = placeholders.PLACEHOLDER_IGNORE_FILE.write_text(
        '[ignore]\n"s/assets/README-template.md" = ["<gone>"]\n'
    )
    assert main(["--apply"]) == 1


def test_rejects_a_non_table_ignore_section(skills: Path) -> None:
    _ = placeholders.PLACEHOLDER_IGNORE_FILE.write_text("ignore = 1\n")
    with pytest.raises(ValueError, match="must be a table"):
        _ = load_ignores()


def test_committed_blocks_match_the_committed_templates() -> None:
    """The real tree: drift here is what CI must catch."""
    assert stale_ignores(load_ignores()) == []
    assert sync_blocks(apply=False) == []
