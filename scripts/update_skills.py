"""Fetch the skills declared in `upstream-skills.toml` into `skills/`.

Run as a module from the repository root, so `scripts` is importable:
`uv run python -m scripts.update_skills` (or `mise run skills-update`).

Every fetched directory is committed to this repository, so a re-fetch
shows up as a reviewable git diff. Skills declared under `local` in the
manifest are maintained by hand here and left untouched.

This script does the deterministic half of vendoring: fetch, rename the
directory and the `name:` frontmatter field, apply the manifest's other
declared frontmatter overrides, replay `skill-rewrites.toml`, then report
every surviving reference to a renamed skill's upstream name.
Triaging that report is an agent's job, described in AGENTS.md.

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
from scripts.frontmatter import FrontmatterError, apply_fields, render, set_field
from scripts.manifest import Manifest, SkillEntry, load_manifest
from scripts.paths import DISABLED_DIR, SKILLS_DIR
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

# Both npm packages are pinned to an exact version, for the same reason
# every tool in `.mise.toml` is: `npm install -g foo` and `npx -y foo`
# both resolve to *latest*, so an upstream compromise would be
# auto-downloaded and executed here — by the very script that writes the
# vendored `skills/` tree. Pinning does not authenticate a release, but it
# fixes *which* one runs, and every fetch lands as a reviewable git diff.
#
# Nothing refreshes these: dependabot covers uv and GitHub Actions, and
# mise covers `[tools]`, but neither sees these. Bump them deliberately,
# keeping to the 7-day-old floor that `minimum_release_age` applies to
# mise tools, and read the resulting `skills/` diff.
SKILLS_CLI_VERSION = "1.5.22"
AGENT_BROWSER_VERSION = "0.33.2"

# How many example lines to print per renamed skill in the reference report.
REPORT_SAMPLE = 3


def skill_dir(local_name: str, *, enabled: bool) -> Path:
    """Return where a skill belongs: `skills/<name>` if enabled, else `disabled/<name>`.

    Whether a skill is active is a manifest decision (the `enabled` field,
    defaulting to false), not a filesystem one — this is the single place
    that turns that decision into a path, so fetching and migration agree.
    """
    if enabled:
        return SKILLS_DIR / local_name
    return DISABLED_DIR / local_name


def skills_command() -> list[str]:
    """Return the argv prefix for the skills.sh CLI.

    A `skills` already on PATH is used as-is and may be any version —
    `install_cli` only installs when the command is missing, so it cannot
    vouch for one it did not put there. The `npx` fallback is pinned.
    """
    if command_exists("skills"):
        return ["skills"]
    return ["npx", "-y", f"skills@{SKILLS_CLI_VERSION}"]


def install_cli(*, dry_run: bool = False) -> bool:
    """Install the skills.sh CLI globally so `skills` is on PATH."""
    if command_exists("skills"):
        success("skills CLI already installed")
        return True

    info(f"Installing the skills.sh CLI (skills@{SKILLS_CLI_VERSION})...")
    if npm_install_global(f"skills@{SKILLS_CLI_VERSION}", dry_run=dry_run):
        success("skills CLI installed")
        return True

    warn(f"Failed to install the skills CLI; falling back to `npx skills@{SKILLS_CLI_VERSION}`")
    return False


def install_agent_browser(*, dry_run: bool = False) -> None:
    """Install the CLI that the agent-browser skill drives.

    npm blocks the package's postinstall script by default, and
    `npm_install_global` passes `--ignore-scripts` on top of that, so fetch
    its Chrome build (~180 MB, once) explicitly.
    """
    if command_exists("agent-browser"):
        success("agent-browser already installed")
    else:
        info(f"Installing agent-browser@{AGENT_BROWSER_VERSION}...")
        if not npm_install_global(f"agent-browser@{AGENT_BROWSER_VERSION}", dry_run=dry_run):
            warn("Failed to install agent-browser; its skill will not work")
            return
        success("agent-browser installed")

    if run(["agent-browser", "install"], dry_run=dry_run) != 0:
        warn("`agent-browser install` failed; run it by hand to fetch Chrome")


def rename_frontmatter(skill_md: Path, local_name: str) -> bool:
    """Set the `name:` frontmatter field to `local_name`. Returns True on success.

    Agents match a skill's directory against its declared name, so a renamed
    directory with an upstream `name:` is a broken skill, not a cosmetic flaw.
    A `SKILL.md` with no `name:` at all is broken too, so it is an error
    rather than something to fill in.
    """
    if not skill_md.is_file():
        error(f"{skill_md} does not exist; cannot rename its frontmatter")
        return False

    text = skill_md.read_text()
    try:
        updated = set_field(text, "name", local_name, require_existing=True)
    except FrontmatterError as exc:
        error(f"{skill_md}: {exc}")
        return False

    if updated != text:
        skill_md.write_text(updated)
    return True


def override_frontmatter(skill_md: Path, entry: SkillEntry) -> bool:
    """Apply the manifest's frontmatter overrides for `entry`. True on success."""
    fields = entry.frontmatter_fields
    if not fields:
        return True

    try:
        apply_fields(skill_md, fields)
    except FrontmatterError as exc:
        error(str(exc))
        return False

    declared = ", ".join(f"{key}: {render(value)}" for key, value in fields.items())
    info(f"  frontmatter: {declared}")
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

    destination = skill_dir(entry.local_name, enabled=entry.enabled)
    stale = skill_dir(entry.local_name, enabled=not entry.enabled)
    if stale.exists():
        shutil.rmtree(stale)
    if destination.exists():
        shutil.rmtree(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(fetched), str(destination))

    skill_md = destination / "SKILL.md"
    if entry.renamed and not rename_frontmatter(skill_md, entry.local_name):
        return False
    if not override_frontmatter(skill_md, entry):
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
        if skill_dir(entry.local_name, enabled=entry.enabled).is_dir():
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


def _candidate_skill_dirs(root: Path) -> list[Path]:
    """List directories directly under `root` that could each be one skill."""
    if not root.is_dir():
        return []
    return [p for p in root.iterdir() if p.is_dir() and not p.is_symlink()]


def undeclared_skills(manifest: Manifest) -> list[Path]:
    """Return skill directories that the manifest does not account for.

    Checks both `skills/` and `disabled/`, since a skill lives in one or the
    other depending on its `enabled` state. Symlinks are skipped. A symlinked
    skill directory is not vendored here — it points at a checkout elsewhere,
    deliberately outside the manifest (see `skills/sbp-brandbook`) — so
    reporting it is noise, and `--prune` would only crash on it, since
    `shutil.rmtree` refuses a symlink.
    """
    declared = manifest.declared_names
    candidates = _candidate_skill_dirs(SKILLS_DIR) + _candidate_skill_dirs(DISABLED_DIR)
    return sorted(p for p in candidates if p.name not in declared)


def sync_skill_locations(manifest: Manifest, *, dry_run: bool = False) -> None:
    """Move every declared skill directory to match its `enabled` state.

    `enabled` is a manifest decision; the filesystem lags behind it until
    this runs. A skill toggled off moves from `skills/<name>` to
    `disabled/<name>`, and back again if toggled on — via `git mv`
    equivalent, never by hand.
    """
    pairs = [(entry.local_name, entry.enabled) for entry in manifest.entries]
    pairs += [(local.name, local.enabled) for local in manifest.local_skills]

    for name, enabled in pairs:
        current = skill_dir(name, enabled=not enabled)
        target = skill_dir(name, enabled=enabled)
        if not current.is_dir() or current.is_symlink():
            continue
        if dry_run:
            dry(f"would move {current} -> {target}")
            continue
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(current), str(target))
        state = "enabled" if enabled else "disabled"
        success(f"Moved {current} -> {target} ({state})")


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
    sync_skill_locations(manifest, dry_run=args.dry_run)
    ok = fetch_skills(manifest.entries, rules, update=args.update, dry_run=args.dry_run)
    prune_skills(manifest, prune=args.prune, dry_run=args.dry_run)

    if not args.dry_run:
        report_references(scan_references(manifest.entries))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
