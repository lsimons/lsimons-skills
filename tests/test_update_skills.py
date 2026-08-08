"""Tests for `scripts.update_skills`."""

from pathlib import Path

import pytest

from scripts import update_skills
from scripts.manifest import SkillEntry

ENTRY = SkillEntry("https://example.com/repo", "demo-skill")
BROWSER_ENTRY = SkillEntry("https://example.com/agent-browser", "agent-browser")


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

    def fake(entry: SkillEntry, staging: Path) -> bool:
        return ok

    monkeypatch.setattr(update_skills, "fetch_skill", fake)


def test_skills_command_prefers_the_installed_cli(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
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


def test_pending_skills_skips_present_directories(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    (tmp_path / "present").mkdir()

    entries = [SkillEntry("https://example.com/a", "present"), ENTRY]
    assert update_skills.pending_skills(entries, update=False) == [ENTRY]


def test_pending_skills_returns_everything_when_updating(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    (tmp_path / "present").mkdir()

    entries = [SkillEntry("https://example.com/a", "present"), ENTRY]
    assert update_skills.pending_skills(entries, update=True) == entries


def test_fetch_skill_moves_the_staged_directory_into_place(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skills_dir = tmp_path / "skills"
    skills_dir.mkdir()
    monkeypatch.setattr(update_skills, "SKILLS_DIR", skills_dir)
    stub_commands(monkeypatch, present=True)

    staging = tmp_path / "staging"
    staged = staging / ".claude" / "skills" / ENTRY.name
    staged.mkdir(parents=True)
    (staged / "SKILL.md").write_text("fetched\n")
    monkeypatch.setattr(update_skills, "run", FakeRun())

    assert update_skills.fetch_skill(ENTRY, staging)
    assert (skills_dir / ENTRY.name / "SKILL.md").read_text() == "fetched\n"


def test_fetch_skill_replaces_an_existing_directory(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    skills_dir = tmp_path / "skills"
    existing = skills_dir / ENTRY.name
    existing.mkdir(parents=True)
    (existing / "stale.md").write_text("stale\n")
    monkeypatch.setattr(update_skills, "SKILLS_DIR", skills_dir)
    stub_commands(monkeypatch, present=True)

    staging = tmp_path / "staging"
    staged = staging / ".claude" / "skills" / ENTRY.name
    staged.mkdir(parents=True)
    (staged / "SKILL.md").write_text("fresh\n")
    monkeypatch.setattr(update_skills, "run", FakeRun())

    assert update_skills.fetch_skill(ENTRY, staging)
    assert not (existing / "stale.md").exists()
    assert (existing / "SKILL.md").read_text() == "fresh\n"


def test_fetch_skill_passes_the_manifest_entry_to_the_cli(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path / "skills")
    stub_commands(monkeypatch, present=True)
    fake = FakeRun(returncode=1)
    monkeypatch.setattr(update_skills, "run", fake)

    assert not update_skills.fetch_skill(ENTRY, tmp_path / "staging")
    assert fake.calls == [
        [
            "skills",
            "add",
            ENTRY.repository,
            "--skill",
            ENTRY.name,
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

    assert not update_skills.fetch_skill(ENTRY, tmp_path / "staging")
    assert "did not produce" in capsys.readouterr().err


def test_fetch_skills_reports_nothing_to_do(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    (tmp_path / ENTRY.name).mkdir()

    assert update_skills.fetch_skills([ENTRY])
    assert "Nothing to fetch." in capsys.readouterr().out


def test_fetch_skills_dry_run_changes_nothing(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    fake = FakeRun()
    monkeypatch.setattr(update_skills, "run", fake)

    assert update_skills.fetch_skills([ENTRY], dry_run=True)
    assert fake.calls == []
    assert list(tmp_path.iterdir()) == []
    assert f"would fetch '{ENTRY.name}'" in capsys.readouterr().out


def test_fetch_skills_fetches_each_pending_entry(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    fetched: list[SkillEntry] = []

    def fake(entry: SkillEntry, staging: Path) -> bool:
        fetched.append(entry)
        return True

    monkeypatch.setattr(update_skills, "fetch_skill", fake)

    assert update_skills.fetch_skills([ENTRY])
    assert fetched == [ENTRY]


def test_fetch_skills_installs_agent_browser_only_when_declared(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    installed: list[bool] = []

    def fake(*, dry_run: bool = False) -> None:
        installed.append(True)

    monkeypatch.setattr(update_skills, "install_agent_browser", fake)

    update_skills.fetch_skills([ENTRY], dry_run=True)
    assert installed == []

    update_skills.fetch_skills([BROWSER_ENTRY], dry_run=True)
    assert installed == [True]


def test_fetch_skills_reports_a_failed_fetch(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    monkeypatch.setattr(update_skills, "SKILLS_DIR", tmp_path)
    stub_fetch_skill(monkeypatch, ok=False)

    assert not update_skills.fetch_skills([ENTRY])


def test_main_dry_run_succeeds_against_the_real_manifest(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    stub_commands(monkeypatch, present=True)
    fake = FakeRun()
    monkeypatch.setattr(update_skills, "run", fake)

    assert update_skills.main(["--dry-run", "--update"]) == 0
    # The only command an --dry-run run may reach is agent-browser's own
    # installer, which the fake swallows without touching the network.
    assert fake.calls == [["agent-browser", "install"]]
    assert "would fetch" in capsys.readouterr().out


def test_main_returns_nonzero_when_a_fetch_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stub_commands(monkeypatch, present=True)

    def fake(entries: list[SkillEntry], *, update: bool = False, dry_run: bool = False) -> bool:
        return False

    monkeypatch.setattr(update_skills, "fetch_skills", fake)

    assert update_skills.main([]) == 1
