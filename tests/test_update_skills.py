"""Tests for `scripts.update_skills`."""

from pathlib import Path

import pytest

from scripts import update_skills
from scripts.manifest import Manifest, SkillEntry, Source
from scripts.references import Reference
from scripts.rewrites import RewriteRules

ENTRY = SkillEntry("https://example.com/repo", "demo-skill", "demo-skill")
RENAMED = SkillEntry("https://example.com/repo", "demo-skill", "x-demo-skill")
BROWSER_ENTRY = SkillEntry("https://example.com/agent-browser", "agent-browser", "agent-browser")
NO_RULES: RewriteRules = {}


class FakeRun:
    """Stands in for `scripts.shell.run`, recording argv and returning a status."""

    def __init__(self, returncode: int = 0) -> None:
        self.returncode = returncode
        self.calls: list[list[str]] = []

    def __call__(self, cmd: list[str], *, dry_run: bool = False, cwd: Path | None = None) -> int:
        self.calls.append(cmd)
        return self.returncode


def stub_commands(monkeypatch: pytest.MonkeyPatch, *, present: bool) -> None:
    """Force `command_exists` to report every command as present/absent."""

    def fake(cmd: str) -> bool:
        return present

    monkeypatch.setattr(update_skills, "command_exists", fake)


def stub_npm(monkeypatch: pytest.MonkeyPatch, *, ok: bool) -> None:
    """Replace `npm_install_global` with a stub reporting success/failure."""

    def fake(package: str, *, dry_run: bool = False) -> bool:
        return ok

    monkeypatch.setattr(update_skills, "npm_install_global", fake)


def forbid_npm(monkeypatch: pytest.MonkeyPatch) -> None:
    """Fail the test if anything tries to install an npm package."""

    def fake(package: str, *, dry_run: bool = False) -> bool:
        pytest.fail(f"unexpected npm install of {package}")

    monkeypatch.setattr(update_skills, "npm_install_global", fake)


def stub_fetch_skill(monkeypatch: pytest.MonkeyPatch, *, ok: bool) -> None:
    """Replace `fetch_skill` with a stub reporting success/failure."""

    def fake(entry: SkillEntry, staging: Path, rules: RewriteRules) -> bool:
        return ok

    monkeypatch.setattr(update_skills, "fetch_skill", fake)


def stage(tmp_path: Path, entry: SkillEntry, body: str = "fetched\n") -> Path:
    """Create the directory layout the skills.sh CLI would produce."""
    staging = tmp_path / "staging"
    staged = staging / ".claude" / "skills" / entry.upstream_name
    staged.mkdir(parents=True)
    (staged / "SKILL.md").write_text(body)
    return staging


def test_skills_command_prefers_the_installed_cli(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_commands(monkeypatch, present=True)
    assert update_skills.skills_command() == ["skills"]


def test_skills_command_falls_back_to_npx(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_commands(monkeypatch, present=False)
    assert update_skills.skills_command() == ["npx", "-y", "skills"]


def test_install_cli_is_a_no_op_when_present(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_commands(monkeypatch, present=True)
    forbid_npm(monkeypatch)
    assert update_skills.install_cli()


def test_install_cli_installs_when_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_commands(monkeypatch, present=False)
    stub_npm(monkeypatch, ok=True)
    assert update_skills.install_cli()


def test_install_cli_warns_when_install_fails(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stub_commands(monkeypatch, present=False)
    stub_npm(monkeypatch, ok=False)

    assert not update_skills.install_cli()
    assert "falling back to `npx skills`" in capsys.readouterr().out


def test_install_agent_browser_fetches_chrome_when_already_installed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stub_commands(monkeypatch, present=True)
    fake = FakeRun()
    monkeypatch.setattr(update_skills, "run", fake)

    update_skills.install_agent_browser()
    assert fake.calls == [["agent-browser", "install"]]


def test_install_agent_browser_gives_up_when_npm_fails(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stub_commands(monkeypatch, present=False)
    stub_npm(monkeypatch, ok=False)
    fake = FakeRun()
    monkeypatch.setattr(update_skills, "run", fake)

    update_skills.install_agent_browser()
    assert fake.calls == []
    assert "its skill will not work" in capsys.readouterr().out


def test_install_agent_browser_warns_when_chrome_fetch_fails(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stub_commands(monkeypatch, present=True)
    monkeypatch.setattr(update_skills, "run", FakeRun(returncode=1))

    update_skills.install_agent_browser()
    assert "run it by hand to fetch Chrome" in capsys.readouterr().out


def test_rename_frontmatter_rewrites_the_name_field(tmp_path: Path) -> None:
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("---\nname: old\ndescription: keeps its name: colon\n---\n\nbody\n")

    assert update_skills.rename_frontmatter(skill_md, "x-old")
    assert skill_md.read_text() == (
        "---\nname: x-old\ndescription: keeps its name: colon\n---\n\nbody\n"
    )


def test_rename_frontmatter_is_idempotent(tmp_path: Path) -> None:
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("---\nname: x-old\n---\n")

    assert update_skills.rename_frontmatter(skill_md, "x-old")
    assert skill_md.read_text() == "---\nname: x-old\n---\n"


def test_override_frontmatter_applies_declared_fields(tmp_path: Path) -> None:
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("---\nname: demo-skill\n---\n\nbody\n")
    entry = ENTRY._replace(frontmatter=(("disable-model-invocation", True),))

    assert update_skills.override_frontmatter(skill_md, entry)
    assert skill_md.read_text() == (
        "---\nname: demo-skill\ndisable-model-invocation: true\n---\n\nbody\n"
    )


def test_override_frontmatter_does_nothing_without_declared_fields(tmp_path: Path) -> None:
    assert update_skills.override_frontmatter(tmp_path / "absent.md", ENTRY)


def test_override_frontmatter_fails_loudly_on_an_uneditable_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("no frontmatter here\n")
    entry = ENTRY._replace(frontmatter=(("disable-model-invocation", True),))

    assert not update_skills.override_frontmatter(skill_md, entry)
    assert "does not start with" in capsys.readouterr().err


def test_rename_frontmatter_fails_loudly_without_a_name_field(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    skill_md = tmp_path / "SKILL.md"
    skill_md.write_text("---\ndescription: nameless\n---\n")

    assert not update_skills.rename_frontmatter(skill_md, "x-old")
    assert "no 'name:' frontmatter field" in capsys.readouterr().err


def test_rename_frontmatter_fails_loudly_without_a_file(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert not update_skills.rename_frontmatter(tmp_path / "absent.md", "x-old")
    assert "does not exist" in capsys.readouterr().err


def test_pending_skills_skips_present_directories(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    (tmp_path / "present").mkdir()

    entries = [SkillEntry("https://example.com/a", "present", "present"), ENTRY]
    assert update_skills.pending_skills(entries, update=False) == [ENTRY]


def test_pending_skills_checks_the_local_name_not_the_upstream_one(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    (tmp_path / RENAMED.local_name).mkdir()

    assert update_skills.pending_skills([RENAMED], update=False) == []


def test_pending_skills_returns_everything_when_updating(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    (tmp_path / "present").mkdir()

    entries = [SkillEntry("https://example.com/a", "present", "present"), ENTRY]
    assert update_skills.pending_skills(entries, update=True) == entries


def test_fetch_skill_moves_the_staged_directory_into_place(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    monkeypatch.setattr(update_skills, "SKILLS_DIR", skills_dir)
    stub_commands(monkeypatch, present=True)
    monkeypatch.setattr(update_skills, "run", FakeRun())

    assert update_skills.fetch_skill(ENTRY, stage(tmp_path, ENTRY), NO_RULES)
    assert (skills_dir / ENTRY.local_name / "SKILL.md").read_text() == "fetched\n"


def test_fetch_skill_installs_a_renamed_skill_under_its_local_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    monkeypatch.setattr(update_skills, "SKILLS_DIR", skills_dir)
    stub_commands(monkeypatch, present=True)
    monkeypatch.setattr(update_skills, "run", FakeRun())
    staging = stage(tmp_path, RENAMED, "---\nname: demo-skill\n---\n\nbody\n")

    assert update_skills.fetch_skill(RENAMED, staging, NO_RULES)
    assert not (skills_dir / RENAMED.upstream_name).exists()
    assert (skills_dir / RENAMED.local_name / "SKILL.md").read_text() == (
        "---\nname: x-demo-skill\n---\n\nbody\n"
    )


def test_fetch_skill_fails_when_the_frontmatter_cannot_be_renamed(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path / "skills")
    (tmp_path / "skills").mkdir()
    stub_commands(monkeypatch, present=True)
    monkeypatch.setattr(update_skills, "run", FakeRun())

    assert not update_skills.fetch_skill(RENAMED, stage(tmp_path, RENAMED, "no frontmatter\n"), {})


def test_fetch_skill_replays_the_rewrite_rules(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    monkeypatch.setattr(update_skills, "SKILLS_DIR", skills_dir)
    stub_commands(monkeypatch, present=True)
    monkeypatch.setattr(update_skills, "run", FakeRun())
    rules: RewriteRules = {ENTRY.local_name: {"SKILL.md": [("fetched", "rewritten")]}}

    assert update_skills.fetch_skill(ENTRY, stage(tmp_path, ENTRY), rules)
    assert (skills_dir / ENTRY.local_name / "SKILL.md").read_text() == "rewritten\n"


def test_fetch_skill_reports_a_stale_rewrite_rule(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A rule that no longer matches means upstream moved; that must be visible."""
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    monkeypatch.setattr(update_skills, "SKILLS_DIR", skills_dir)
    stub_commands(monkeypatch, present=True)
    monkeypatch.setattr(update_skills, "run", FakeRun())
    rules: RewriteRules = {ENTRY.local_name: {"SKILL.md": [("absent", "rewritten")]}}

    assert not update_skills.fetch_skill(ENTRY, stage(tmp_path, ENTRY), rules)
    assert "stale rewrite rule" in capsys.readouterr().out


def test_fetch_skill_replaces_an_existing_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skills_dir = tmp_path / "skills"
    existing = skills_dir / ENTRY.local_name
    existing.mkdir(parents=True)
    (existing / "stale.md").write_text("stale\n")
    monkeypatch.setattr(update_skills, "SKILLS_DIR", skills_dir)
    stub_commands(monkeypatch, present=True)
    monkeypatch.setattr(update_skills, "run", FakeRun())

    assert update_skills.fetch_skill(ENTRY, stage(tmp_path, ENTRY, "fresh\n"), NO_RULES)
    assert not (existing / "stale.md").exists()
    assert (existing / "SKILL.md").read_text() == "fresh\n"


def test_fetch_skill_asks_the_cli_for_the_upstream_name(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path / "skills")
    stub_commands(monkeypatch, present=True)
    fake = FakeRun(returncode=1)
    monkeypatch.setattr(update_skills, "run", fake)

    assert not update_skills.fetch_skill(RENAMED, tmp_path / "staging", NO_RULES)
    assert fake.calls == [
        [
            "skills",
            "add",
            RENAMED.repository,
            "--skill",
            RENAMED.upstream_name,
            "--agent",
            "claude-code",
            "--copy",
            "--yes",
        ]
    ]


def test_fetch_skill_fails_when_the_cli_produces_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path / "skills")
    stub_commands(monkeypatch, present=True)
    monkeypatch.setattr(update_skills, "run", FakeRun())

    assert not update_skills.fetch_skill(ENTRY, tmp_path / "staging", NO_RULES)
    assert "did not produce" in capsys.readouterr().err


def test_fetch_skills_reports_nothing_to_do(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    (tmp_path / ENTRY.local_name).mkdir()

    assert update_skills.fetch_skills([ENTRY], NO_RULES)
    assert "Nothing to fetch." in capsys.readouterr().out


def test_fetch_skills_dry_run_changes_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    fake = FakeRun()
    monkeypatch.setattr(update_skills, "run", fake)

    assert update_skills.fetch_skills([RENAMED], NO_RULES, dry_run=True)
    assert fake.calls == []
    assert list(tmp_path.iterdir()) == []
    out = capsys.readouterr().out
    assert f"would fetch '{RENAMED.upstream_name}'" in out
    assert f"as '{RENAMED.local_name}'" in out


def test_fetch_skills_fetches_each_pending_entry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    fetched: list[SkillEntry] = []

    def fake(entry: SkillEntry, staging: Path, rules: RewriteRules) -> bool:
        fetched.append(entry)
        return True

    monkeypatch.setattr(update_skills, "fetch_skill", fake)

    assert update_skills.fetch_skills([ENTRY], NO_RULES)
    assert fetched == [ENTRY]


def test_fetch_skills_installs_agent_browser_only_when_declared(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    installed: list[bool] = []

    def fake(*, dry_run: bool = False) -> None:
        installed.append(True)

    monkeypatch.setattr(update_skills, "install_agent_browser", fake)

    update_skills.fetch_skills([ENTRY], NO_RULES, dry_run=True)
    assert installed == []

    update_skills.fetch_skills([BROWSER_ENTRY], NO_RULES, dry_run=True)
    assert installed == [True]


def test_fetch_skills_reports_a_failed_fetch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    stub_fetch_skill(monkeypatch, ok=False)

    assert not update_skills.fetch_skills([ENTRY], NO_RULES)


def make_manifest(*local: str) -> Manifest:
    source = Source("https://example.com/repo", "", "MIT", "Copyright (c) 2026 Nobody", [ENTRY])
    return Manifest(sources=[source], local_skills=list(local))


def test_undeclared_skills_ignores_declared_and_hand_maintained_directories(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    for name in (ENTRY.local_name, "by-hand", "leftover"):
        (tmp_path / name).mkdir()

    assert [p.name for p in update_skills.undeclared_skills(make_manifest("by-hand"))] == [
        "leftover"
    ]


def test_undeclared_skills_ignores_symlinked_directories(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    """A symlinked skill lives in another checkout and is not ours to prune."""
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path / "skills")
    (tmp_path / "skills").mkdir()
    elsewhere = tmp_path / "elsewhere" / "linked"
    elsewhere.mkdir(parents=True)
    (tmp_path / "skills" / "linked").symlink_to(elsewhere, target_is_directory=True)

    assert update_skills.undeclared_skills(make_manifest()) == []


def test_undeclared_skills_tolerates_a_missing_skills_dir(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path / "absent")
    assert update_skills.undeclared_skills(make_manifest()) == []


def test_prune_only_warns_without_the_flag(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A stray directory could be a hand-maintained skill; never delete silently."""
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    (tmp_path / "leftover").mkdir()

    update_skills.prune_skills(make_manifest(), prune=False)

    assert (tmp_path / "leftover").is_dir()
    assert "use --prune to delete" in capsys.readouterr().out


def test_prune_deletes_undeclared_directories(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    (tmp_path / "leftover").mkdir()

    update_skills.prune_skills(make_manifest(), prune=True)

    assert not (tmp_path / "leftover").exists()


def test_prune_dry_run_deletes_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    (tmp_path / "leftover").mkdir()

    update_skills.prune_skills(make_manifest(), prune=True, dry_run=True)

    assert (tmp_path / "leftover").is_dir()
    assert "would delete" in capsys.readouterr().out


def test_report_references_is_quiet_when_clean(capsys: pytest.CaptureFixture[str]) -> None:
    update_skills.report_references([])
    assert "No references" in capsys.readouterr().out


def test_report_references_samples_each_group(capsys: pytest.CaptureFixture[str]) -> None:
    found = [
        Reference(update_skills.SKILLS_DIR / "a" / "SKILL.md", n, "tdd", ("mp-tdd",), f"line {n}")
        for n in range(1, update_skills.REPORT_SAMPLE + 3)
    ]

    update_skills.report_references(found)

    out = capsys.readouterr().out
    assert "tdd -> mp-tdd" in out
    assert "skills/a/SKILL.md:1: line 1" in out
    assert "... and 2 more" in out


def test_main_dry_run_succeeds_against_the_real_manifest(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stub_commands(monkeypatch, present=True)
    fake = FakeRun()
    monkeypatch.setattr(update_skills, "run", fake)

    assert update_skills.main(["--dry-run", "--update"]) == 0
    # The only command a --dry-run run may reach is agent-browser's own
    # installer, which the fake swallows without touching the network.
    assert fake.calls == [["agent-browser", "install"]]
    assert "would fetch" in capsys.readouterr().out


def test_main_returns_nonzero_when_a_fetch_fails(monkeypatch: pytest.MonkeyPatch) -> None:
    stub_commands(monkeypatch, present=True)

    def fake(
        entries: list[SkillEntry],
        rules: RewriteRules,
        *,
        update: bool = False,
        dry_run: bool = False,
    ) -> bool:
        return False

    monkeypatch.setattr(update_skills, "fetch_skills", fake)

    assert update_skills.main([]) == 1


def test_report_references_flags_an_ambiguous_name(capsys: pytest.CaptureFixture[str]) -> None:
    found = [
        Reference(
            update_skills.SKILLS_DIR / "a" / "SKILL.md", 1, "tdd", ("ao-tdd", "s-tdd"), "line"
        )
    ]

    update_skills.report_references(found)

    assert "ao-tdd | s-tdd AMBIGUOUS" in capsys.readouterr().out
