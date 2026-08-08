"""Tests for `scripts.frontmatter`."""

from pathlib import Path

import pytest

from scripts.frontmatter import (
    FrontmatterError,
    apply_fields,
    field_value,
    render,
    set_field,
    split,
)

SKILL = "---\nname: demo\ndescription: does things\n---\n\n# Demo\n\nbody\n"


def test_split_separates_the_block_from_the_body() -> None:
    block, rest = split(SKILL)
    assert block == ["name: demo\n", "description: does things\n"]
    assert rest == ["---\n", "\n", "# Demo\n", "\n", "body\n"]


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("# Demo\n\nbody\n", "does not start with"),
        ("", "does not start with"),
        ("---\nname: demo\n", "never closed"),
    ],
)
def test_split_rejects_a_missing_or_unclosed_block(text: str, message: str) -> None:
    with pytest.raises(FrontmatterError, match=message):
        split(text)


def test_set_field_replaces_an_existing_field_in_place() -> None:
    assert set_field(SKILL, "name", "x-demo") == SKILL.replace("name: demo", "name: x-demo")


def test_set_field_appends_a_new_field_to_the_end_of_the_block() -> None:
    assert set_field(SKILL, "disable-model-invocation", True) == SKILL.replace(
        "description: does things\n---",
        "description: does things\ndisable-model-invocation: true\n---",
    )


def test_set_field_leaves_the_body_untouched() -> None:
    body = "---\nname: demo\n---\n\nname: not frontmatter\n"
    assert set_field(body, "name", "x-demo") == "---\nname: x-demo\n---\n\nname: not frontmatter\n"


def test_set_field_is_idempotent() -> None:
    once = set_field(SKILL, "disable-model-invocation", True)
    assert set_field(once, "disable-model-invocation", True) == once


def test_set_field_requires_an_existing_field_when_asked() -> None:
    with pytest.raises(FrontmatterError, match="no 'other:' frontmatter field"):
        set_field(SKILL, "other", "value", require_existing=True)


def test_set_field_refuses_to_rewrite_a_multi_line_value() -> None:
    text = "---\nname: demo\ndescription: >\n  a folded\n  description\n---\n"
    with pytest.raises(FrontmatterError, match="multi-line value"):
        set_field(text, "description", "flat")


@pytest.mark.parametrize(("value", "expected"), [(True, "true"), (False, "false"), ("x", "x")])
def test_render_writes_yaml_scalars(value: str | bool, expected: str) -> None:
    assert render(value) == expected


def test_apply_fields_writes_and_reports_the_change(tmp_path: Path) -> None:
    path = tmp_path / "SKILL.md"
    path.write_text(SKILL)

    assert apply_fields(path, {"disable-model-invocation": True})
    assert field_value(path.read_text(), "disable-model-invocation") == "true"
    assert not apply_fields(path, {"disable-model-invocation": True})


def test_apply_fields_names_the_file_it_could_not_edit(tmp_path: Path) -> None:
    path = tmp_path / "SKILL.md"
    path.write_text("no frontmatter here\n")

    with pytest.raises(FrontmatterError, match=r"SKILL\.md: file does not start with"):
        apply_fields(path, {"disable-model-invocation": True})


def test_apply_fields_rejects_a_missing_file(tmp_path: Path) -> None:
    with pytest.raises(FrontmatterError, match="does not exist"):
        apply_fields(tmp_path / "absent.md", {"a": "b"})


def test_field_value_reports_absent_fields() -> None:
    assert field_value(SKILL, "name") == "demo"
    assert field_value(SKILL, "disable-model-invocation") is None
