"""Tests for `scripts.manifest`."""

from pathlib import Path

import pytest

from scripts.frontmatter import field_value, render
from scripts.manifest import LocalSkill, SkillEntry, load_manifest, local_name_for
from scripts.paths import UPSTREAM_MANIFEST
from scripts.update_skills import skill_dir, undeclared_skills

MINIMAL_SOURCE = """
[[source]]
repository = "https://example.com/a"
license = "MIT"
copyright = "Copyright (c) 2026 Nobody"
skills = ["first", "second"]
"""


def write_manifest(tmp_path: Path, content: str) -> Path:
    path = tmp_path / "upstream-skills.toml"
    path.write_text(content)
    return path


def test_parses_entries_in_manifest_order(tmp_path: Path) -> None:
    manifest = load_manifest(write_manifest(tmp_path, MINIMAL_SOURCE))
    assert manifest.entries == [
        SkillEntry("https://example.com/a", "first", "first"),
        SkillEntry("https://example.com/a", "second", "second"),
    ]
    assert manifest.sources[0].license == "MIT"


def test_prefix_applies_to_every_skill(tmp_path: Path) -> None:
    manifest = load_manifest(
        write_manifest(tmp_path, MINIMAL_SOURCE.replace("[[source]]", '[[source]]\nprefix = "x-"'))
    )
    assert [e.local_name for e in manifest.entries] == ["x-first", "x-second"]
    assert all(e.renamed for e in manifest.entries)


def test_prefix_is_not_applied_twice(tmp_path: Path) -> None:
    """An upstream that already namespaces a skill keeps the name it has."""
    manifest = load_manifest(
        write_manifest(
            tmp_path,
            MINIMAL_SOURCE.replace('skills = ["first", "second"]', 'skills = ["x-first"]').replace(
                "[[source]]", '[[source]]\nprefix = "x-"'
            ),
        )
    )
    assert manifest.entries == [SkillEntry("https://example.com/a", "x-first", "x-first")]
    assert not manifest.entries[0].renamed


def test_rename_overrides_prefix(tmp_path: Path) -> None:
    manifest = load_manifest(
        write_manifest(
            tmp_path,
            MINIMAL_SOURCE.replace(
                "[[source]]", '[[source]]\nprefix = "x-"\nrename = { first = "custom" }'
            ),
        )
    )
    assert [e.local_name for e in manifest.entries] == ["custom", "x-second"]


def test_local_skills_are_declared_but_not_fetched(tmp_path: Path) -> None:
    manifest = load_manifest(write_manifest(tmp_path, 'local = ["by-hand"]\n' + MINIMAL_SOURCE))
    assert manifest.local_skills == [LocalSkill("by-hand")]
    assert "by-hand" not in {e.local_name for e in manifest.entries}
    assert manifest.declared_names == {"by-hand", "first", "second"}
    assert manifest.enabled_names == set()


def test_local_skills_enabled_defaults_to_false(tmp_path: Path) -> None:
    manifest = load_manifest(write_manifest(tmp_path, 'local = ["by-hand"]\n' + MINIMAL_SOURCE))
    assert manifest.local_skills[0].enabled is False


def test_local_skills_enabled_can_be_declared(tmp_path: Path) -> None:
    content = 'local = ["by-hand"]\n[local-enabled]\nby-hand = true\n' + MINIMAL_SOURCE
    manifest = load_manifest(write_manifest(tmp_path, content))
    assert manifest.local_skills == [LocalSkill("by-hand", True)]
    assert manifest.enabled_names == {"by-hand"}


def test_local_enabled_rejects_a_skill_not_in_local(tmp_path: Path) -> None:
    content = 'local = ["by-hand"]\n[local-enabled]\nother = true\n' + MINIMAL_SOURCE
    with pytest.raises(ValueError, match=r"'local-enabled' for skills not listed in 'local'"):
        load_manifest(write_manifest(tmp_path, content))


def test_source_enabled_defaults_to_false(tmp_path: Path) -> None:
    manifest = load_manifest(write_manifest(tmp_path, MINIMAL_SOURCE))
    assert [e.enabled for e in manifest.entries] == [False, False]


def test_source_enabled_can_be_declared(tmp_path: Path) -> None:
    content = MINIMAL_SOURCE + "[source.enabled]\nfirst = true\n"
    manifest = load_manifest(write_manifest(tmp_path, content))
    first, second = manifest.entries
    assert first.enabled is True
    assert second.enabled is False
    assert manifest.enabled_names == {"first"}


def test_source_enabled_rejects_a_skill_not_listed(tmp_path: Path) -> None:
    content = MINIMAL_SOURCE + "[source.enabled]\nthird = true\n"
    with pytest.raises(ValueError, match=r"enabled for skills not listed: \['third'\]"):
        load_manifest(write_manifest(tmp_path, content))


def test_source_enabled_rejects_a_non_boolean_value(tmp_path: Path) -> None:
    content = MINIMAL_SOURCE + '[source.enabled]\nfirst = "yes"\n'
    with pytest.raises(ValueError, match="enabled\\['first'\\] must be a boolean"):
        load_manifest(write_manifest(tmp_path, content))


def test_empty_manifest_yields_no_entries(tmp_path: Path) -> None:
    manifest = load_manifest(write_manifest(tmp_path, "# nothing here\n"))
    assert manifest.entries == []
    assert manifest.declared_names == set()


@pytest.mark.parametrize(
    ("content", "match"),
    [
        ('[[source]]\nskills = ["a"]\n', "missing required key 'repository'"),
        ('[[source]]\nrepository = "r"\nlicense = "MIT"\ncopyright = "c"\n', "'skills'"),
        (MINIMAL_SOURCE.replace('license = "MIT"', "license = 1"), "'license' must be a str"),
        (MINIMAL_SOURCE.replace("[[source]]", "[[source]]\nprefix = 1"), "'prefix' must be"),
        (MINIMAL_SOURCE.replace('"first"', "1"), "only strings"),
        (
            MINIMAL_SOURCE.replace("[[source]]", '[[source]]\nrename = { absent = "x" }'),
            "renames for skills not listed",
        ),
        ('local = "nope"\n', "'local' must be a list"),
    ],
)
def test_rejects_malformed_manifests(tmp_path: Path, content: str, match: str) -> None:
    with pytest.raises(ValueError, match=match):
        load_manifest(write_manifest(tmp_path, content))


def test_rejects_two_sources_claiming_the_same_local_name(tmp_path: Path) -> None:
    content = MINIMAL_SOURCE + MINIMAL_SOURCE.replace("https://example.com/a", "https://other/b")
    with pytest.raises(ValueError, match="'first' is declared twice"):
        load_manifest(write_manifest(tmp_path, content))


def test_rejects_a_source_colliding_with_a_local_skill(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match=r"'first' is declared twice \(by local"):
        load_manifest(write_manifest(tmp_path, 'local = ["first"]\n' + MINIMAL_SOURCE))


def test_parses_frontmatter_overrides(tmp_path: Path) -> None:
    content = MINIMAL_SOURCE + "[source.frontmatter]\nfirst = { disable-model-invocation = true }\n"
    manifest = load_manifest(write_manifest(tmp_path, content))
    first, second = manifest.entries
    assert first.frontmatter_fields == {"disable-model-invocation": True}
    assert second.frontmatter_fields == {}


def test_rejects_frontmatter_for_a_skill_not_listed(tmp_path: Path) -> None:
    content = MINIMAL_SOURCE + "[source.frontmatter]\nthird = { a = true }\n"
    with pytest.raises(ValueError, match=r"frontmatter for skills not listed: \['third'\]"):
        load_manifest(write_manifest(tmp_path, content))


def test_rejects_overriding_the_name_field(tmp_path: Path) -> None:
    content = MINIMAL_SOURCE + '[source.frontmatter]\nfirst = { name = "other" }\n'
    with pytest.raises(ValueError, match="'name' is set by the fetcher"):
        load_manifest(write_manifest(tmp_path, content))


def test_rejects_a_non_scalar_frontmatter_value(tmp_path: Path) -> None:
    content = MINIMAL_SOURCE + "[source.frontmatter]\nfirst = { tags = [1, 2] }\n"
    with pytest.raises(ValueError, match="'tags' must be a string or boolean"):
        load_manifest(write_manifest(tmp_path, content))


@pytest.mark.parametrize(
    ("name", "prefix", "expected"),
    [
        ("thing", "x-", "x-thing"),
        ("x-thing", "x-", "x-thing"),
        ("thing", "", "thing"),
        ("extra-thing", "x-", "x-extra-thing"),
    ],
)
def test_local_name_for(name: str, prefix: str, expected: str) -> None:
    assert local_name_for(name, prefix) == expected


def test_real_manifest_is_parseable_and_fully_vendored() -> None:
    """Every declared skill must be committed under skills/, at its declared location."""
    manifest = load_manifest(UPSTREAM_MANIFEST)
    assert manifest.entries, "expected at least one declared skill"
    missing = sorted(
        n
        for n in manifest.declared_names
        if not skill_dir(n, enabled=n in manifest.enabled_names).is_dir()
    )
    assert missing == []


def test_real_manifest_declares_every_vendored_skill() -> None:
    """No stray directories: `--prune` would delete anything undeclared.

    Symlinks are excluded, matching `update_skills.undeclared_skills`: a
    symlinked skill points at another checkout and is out of the manifest on
    purpose. `disabled/` holds toggled-off skills, not a skill itself.
    """
    manifest = load_manifest(UPSTREAM_MANIFEST)
    assert undeclared_skills(manifest) == []


def test_real_manifest_frontmatter_overrides_are_applied_to_the_vendored_tree() -> None:
    """A declared override must be present in the committed SKILL.md.

    `skills/` is committed, so an override could otherwise drift out of the
    tree — by a hand edit, or by declaring one without re-fetching.
    """
    manifest = load_manifest(UPSTREAM_MANIFEST)
    for entry in manifest.entries:
        fields = entry.frontmatter_fields
        if not fields:
            continue
        destination = skill_dir(entry.local_name, enabled=entry.enabled)
        text = (destination / "SKILL.md").read_text()
        for key, value in fields.items():
            assert field_value(text, key) == render(value), (
                f"{entry.local_name} declares '{key}' but its SKILL.md does not match; "
                f"run `mise run skills-update`"
            )


def test_real_manifest_records_licensing_for_every_source() -> None:
    """Vendoring makes licensing this repository's problem; see AGENTS.md."""
    for source in load_manifest(UPSTREAM_MANIFEST).sources:
        assert source.license, f"{source.repository} declares no license"
        assert source.copyright, f"{source.repository} declares no copyright"
