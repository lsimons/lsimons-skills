"""Fetch the skills declared in `upstream-skills.toml` into `skills/`.

Run as a module from the repository root, so `scripts` is importable:
`uv run python -m scripts.update_skills` (or `mise run skills-update`).

Every fetched directory is committed to this repository, so a re-fetch
shows up as a reviewable git diff. Skills declared under `local` in the
manifest are maintained by hand here and left untouched.

This script does the deterministic half of vendoring: fetch, rename the
directory and the `name:` frontmatter field, replay `skill-rewrites.toml`,
then report every surviving reference to a renamed skill's upstream name.
Triaging that report is an agent's job, described in AGENTS.md.

This script only maintains `skills/`. Wiring that directory into a
specific coding agent's configuration is the job of whatever consumes
this repository (e.g. the dotfiles agent topics).
"""

import argparse
import re
import shutil
import sys
import tempfile
from pathlib import Path

from scripts.console import dry, error, info, success, warn
from scripts.manifest import Manifest, SkillEntry, load_manifest
from scripts.paths import SKILLS_DIR
from scripts.references import Reference, group_by_skill, scan_references
from scripts.rewrites import RewriteRules, apply_rewrites, load_rewrites
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

# How many example lines to print per renamed skill in the reference report.
REPORT_SAMPLE = 3


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


def rename_frontmatter(skill_md: Path, local_name: str) -> bool:
    """Set the `name:` frontmatter field to `local_name`. Returns True if changed.

    Agents match a skill's directory against its declared name, so a renamed
    directory with an upstream `name:` is a broken skill, not a cosmetic flaw.
    """
    if not skill_md.is_file():
        error(f"{skill_md} does not exist; cannot rename its frontmatter")
        return False

    text = skill_md.read_text()
    updated, count = re.subn(
        r"^name:.*$",
        f"name: {local_name}",
        text,
        count=1,
        flags=re.MULTILINE,
    )
    if count == 0:
        error(f"{skill_md} has no 'name:' frontmatter field")
        return False
    if updated == text:
        return False
    skill_md.write_text(updated)
    return True


def fetch_skill(entry: SkillEntry, staging: Path, rules: RewriteRules) -> bool:
    """Fetch one skill into `staging`, then install it under its local name."""
    status = run(
        [
            *skills_command(),
            "add",
            entry.repository,
            "--skill",
            entry.upstream_name,
            "--agent",
            STAGING_AGENT,
            "--copy",
            "--yes",
        ],
        cwd=staging,
    )
    if status != 0:
        error(f"Failed to fetch skill '{entry.upstream_name}' from {entry.repository}")
        return False

    fetched = staging / ".claude" / "skills" / entry.upstream_name
    if not fetched.is_dir():
        error(f"skills CLI did not produce {fetched}")
        return False

    destination = SKILLS_DIR / entry.local_name
    if destination.exists():
        shutil.rmtree(destination)
    shutil.move(str(fetched), str(destination))

    if entry.renamed and not rename_frontmatter(destination / "SKILL.md", entry.local_name):
        return False

    result = apply_rewrites(entry.local_name, destination, rules)
    for rule in result.stale:
        warn(f"stale rewrite rule (text not found): {rule.describe()}")
    detail = f" ({result.replacements} rewrites)" if result.replacements else ""
    success(f"Fetched skill: {destination}{detail}")
    return not result.stale


def pending_skills(entries: list[SkillEntry], *, update: bool) -> list[SkillEntry]:
    """Return the entries that need fetching, reporting the ones that don't."""
    if update:
        return list(entries)

    pending: list[SkillEntry] = []
    for entry in entries:
        if (SKILLS_DIR / entry.local_name).is_dir():
            success(f"Skill already present: {entry.local_name}")
        else:
            pending.append(entry)
    return pending


def fetch_skills(
    entries: list[SkillEntry],
    rules: RewriteRules,
    *,
    update: bool = False,
    dry_run: bool = False,
) -> bool:
    """Fetch every manifest entry that needs it. Returns True on success."""
    if any(entry.upstream_name == AGENT_BROWSER_SKILL for entry in entries):
        install_agent_browser(dry_run=dry_run)

    pending = pending_skills(entries, update=update)
    if not pending:
        info("Nothing to fetch.")
        return True

    if dry_run:
        for entry in pending:
            rename = f" as '{entry.local_name}'" if entry.renamed else ""
            dry(f"would fetch '{entry.upstream_name}' from {entry.repository}{rename}")
        return True

    ok = True
    with tempfile.TemporaryDirectory(prefix="lsimons-skills-") as tmpdir:
        staging = Path(tmpdir)
        for entry in pending:
            info(f"Fetching skill '{entry.upstream_name}' from {entry.repository}...")
            ok = fetch_skill(entry, staging, rules) and ok
    return ok


def undeclared_skills(manifest: Manifest) -> list[Path]:
    """Return skill directories that the manifest does not account for."""
    if not SKILLS_DIR.is_dir():
        return []
    declared = manifest.declared_names
    return sorted(p for p in SKILLS_DIR.iterdir() if p.is_dir() and p.name not in declared)


def prune_skills(manifest: Manifest, *, prune: bool, dry_run: bool = False) -> None:
    """Report — and with `prune`, delete — skill directories not in the manifest.

    Deletion is opt-in because a stale directory is usually a leftover from a
    rename, but could equally be a hand-maintained skill missing its `local`
    declaration. Losing that silently would be unrecoverable.
    """
    for path in undeclared_skills(manifest):
        if not prune:
            warn(f"undeclared skill directory: {path} (use --prune to delete)")
        elif dry_run:
            dry(f"would delete undeclared skill directory: {path}")
        else:
            shutil.rmtree(path)
            success(f"Deleted undeclared skill directory: {path}")


def report_references(references: list[Reference]) -> None:
    """Print the surviving mentions of renamed skills' upstream names."""
    if not references:
        success("No references to renamed skills' upstream names remain.")
        return

    grouped = group_by_skill(references)
    warn(
        f"{len(references)} line(s) still mention the upstream name of a renamed skill, "
        f"across {len(grouped)} name(s). Triage per AGENTS.md, "
        f"then record the real ones in skill-rewrites.toml:"
    )
    for upstream_name, found in grouped.items():
        targets = " | ".join(found[0].local_names)
        ambiguous = " AMBIGUOUS" if found[0].ambiguous else ""
        print(f"  {upstream_name} -> {targets}{ambiguous} ({len(found)} line(s))")
        for reference in found[:REPORT_SAMPLE]:
            relative = reference.path.relative_to(SKILLS_DIR.parent)
            print(f"    {relative}:{reference.lineno}: {reference.line}")
        if len(found) > REPORT_SAMPLE:
            print(f"    ... and {len(found) - REPORT_SAMPLE} more")


def main(argv: list[str] | None = None) -> int:
    """Entry point. Returns a process exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true", help="preview without changing anything")
    parser.add_argument(
        "--update",
        action="store_true",
        help="re-fetch skills that are already present in skills/",
    )
    parser.add_argument(
        "--prune",
        action="store_true",
        help="delete skill directories the manifest does not declare",
    )
    args = parser.parse_args(argv)

    info(f"Updating skills in {SKILLS_DIR}...")
    if not args.dry_run:
        SKILLS_DIR.mkdir(parents=True, exist_ok=True)

    install_cli(dry_run=args.dry_run)

    manifest = load_manifest()
    rules = load_rewrites()
    ok = fetch_skills(manifest.entries, rules, update=args.update, dry_run=args.dry_run)
    prune_skills(manifest, prune=args.prune, dry_run=args.dry_run)

    if not args.dry_run:
        report_references(scan_references(manifest.entries))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
