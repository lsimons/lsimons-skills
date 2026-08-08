"""Fetch the skills declared in `upstream-skills.txt` into `skills/`.

Run as a module from the repository root, so `scripts` is importable:
`uv run python -m scripts.update_skills` (or `mise run skills-update`).

Every fetched directory is committed to this repository, so a re-fetch
shows up as a reviewable git diff. Skills not listed in the manifest are
maintained by hand here and left untouched.

This script only maintains `skills/`. Wiring that directory into a
specific coding agent's configuration is the job of whatever consumes
this repository (e.g. the dotfiles agent topics).
"""

import argparse
import shutil
import sys
import tempfile
from pathlib import Path

from scripts.console import dry, error, info, success, warn
from scripts.manifest import SkillEntry, load_manifest
from scripts.paths import SKILLS_DIR
from scripts.shell import command_exists, npm_install_global, run

# The skills.sh CLI installs into one directory per agent. Ask for
# claude-code's layout (`<cwd>/.claude/skills/<skill>`) inside a staging
# directory and move the result into skills/ ourselves, so the fetch does
# not depend on any agent being configured on this machine.
STAGING_AGENT = "claude-code"

# The agent-browser skill is only a discovery stub: it shells out to the
# `agent-browser` CLI, which serves version-matched instructions and drives
# its own Chrome build.
AGENT_BROWSER_SKILL = "agent-browser"


def skills_command() -> list[str]:
    """Return the argv prefix for the skills.sh CLI."""
    if command_exists("skills"):
        return ["skills"]
    return ["npx", "-y", "skills"]


def install_cli(*, dry_run: bool = False) -> bool:
    """Install the skills.sh CLI globally so `skills` is on PATH."""
    if command_exists("skills"):
        success("skills CLI already installed")
        return True

    info("Installing the skills.sh CLI...")
    if npm_install_global("skills", dry_run=dry_run):
        success("skills CLI installed")
        return True

    warn("Failed to install the skills CLI; falling back to `npx skills`")
    return False


def install_agent_browser(*, dry_run: bool = False) -> None:
    """Install the CLI that the agent-browser skill drives.

    npm blocks the package's postinstall script by default, so fetch its
    Chrome build (~180 MB, once) explicitly.
    """
    if command_exists("agent-browser"):
        success("agent-browser already installed")
    else:
        info("Installing agent-browser...")
        if not npm_install_global("agent-browser", dry_run=dry_run):
            warn("Failed to install agent-browser; its skill will not work")
            return
        success("agent-browser installed")

    if run(["agent-browser", "install"], dry_run=dry_run) != 0:
        warn("`agent-browser install` failed; run it by hand to fetch Chrome")


def fetch_skill(entry: SkillEntry, staging: Path) -> bool:
    """Fetch one skill into `staging` and move it into `skills/`."""
    status = run(
        [
            *skills_command(),
            "add",
            entry.repository,
            "--skill",
            entry.name,
            "--agent",
            STAGING_AGENT,
            "--copy",
            "--yes",
        ],
        cwd=staging,
    )
    if status != 0:
        error(f"Failed to fetch skill '{entry.name}' from {entry.repository}")
        return False

    fetched = staging / ".claude" / "skills" / entry.name
    if not fetched.is_dir():
        error(f"skills CLI did not produce {fetched}")
        return False

    destination = SKILLS_DIR / entry.name
    if destination.exists():
        shutil.rmtree(destination)
    shutil.move(str(fetched), str(destination))
    success(f"Fetched skill: {destination}")
    return True


def pending_skills(entries: list[SkillEntry], *, update: bool) -> list[SkillEntry]:
    """Return the entries that need fetching, reporting the ones that don't."""
    if update:
        return list(entries)

    pending: list[SkillEntry] = []
    for entry in entries:
        if (SKILLS_DIR / entry.name).is_dir():
            success(f"Skill already present: {entry.name}")
        else:
            pending.append(entry)
    return pending


def fetch_skills(
    entries: list[SkillEntry],
    *,
    update: bool = False,
    dry_run: bool = False,
) -> bool:
    """Fetch every manifest entry that needs it. Returns True on success."""
    if any(entry.name == AGENT_BROWSER_SKILL for entry in entries):
        install_agent_browser(dry_run=dry_run)

    pending = pending_skills(entries, update=update)
    if not pending:
        info("Nothing to fetch.")
        return True

    if dry_run:
        for entry in pending:
            dry(f"would fetch '{entry.name}' from {entry.repository} into {SKILLS_DIR}")
        return True

    ok = True
    with tempfile.TemporaryDirectory(prefix="lsimons-skills-") as tmpdir:
        staging = Path(tmpdir)
        for entry in pending:
            info(f"Fetching skill '{entry.name}' from {entry.repository}...")
            ok = fetch_skill(entry, staging) and ok
    return ok


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="preview without changing anything")
    parser.add_argument(
        "--update",
        action="store_true",
        help="re-fetch skills that are already present in skills/",
    )
    args = parser.parse_args(argv)

    info(f"Updating skills in {SKILLS_DIR}...")
    if not args.dry_run:
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    install_cli(dry_run=args.dry_run)

    entries = load_manifest()
    return 0 if fetch_skills(entries, update=args.update, dry_run=args.dry_run) else 1


if __name__ == "__main__":
    sys.exit(main())
