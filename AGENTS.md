# Agent Instructions for lsimons-skills

> This file (`AGENTS.md`) is the canonical agent configuration. `CLAUDE.md` is a symlink to this file.

The single source of truth for my agent skills: Markdown skill definitions under
`skills/`, plus the Python tooling that maintains them.

This repository does **not** configure or install any specific coding agent.
It only maintains `skills/`; consumers (the `lsimons-dotfiles` agent topics)
link that directory into each agent's config.

## Quick Reference

- **One-time**: `mise install`
- **Setup**: `mise run install` (or `uv sync --all-groups`)
- **Test**: `mise run test` (or `uv run pytest`)
- **Lint**: `mise run lint` (or `uv run ruff check . && uv run ruff format --check .`)
- **Typecheck**: `mise run typecheck` (or `uv run basedpyright`)
- **Format**: `mise run format` (or `uv run ruff format . && uv run ruff check --fix .`)
- **Full CI gate**: `mise run ci`
- **Fetch missing skills**: `mise run skills-install`
- **Re-fetch all skills**: `mise run skills-update`

## Structure

```
skills/               # Skill definitions, one directory per skill
scripts/              # Python tooling that maintains skills/
tests/                # Tests for scripts/
upstream-skills.txt   # Manifest of skills fetched from skills.sh
```

There is no installable Python package (`tool.uv.package = false`) —
`scripts` is imported directly via `pythonpath = ["."]` in pytest config,
so run the tooling as a module from the repository root:
`uv run python -m scripts.update_skills`.

## Skills

Everything under `skills/` is committed, including skills fetched from
skills.sh. `upstream-skills.txt` declares what is fetched; skills absent from
that manifest (`1password`, `claude-history`, `python-knowledge-patch`) are
maintained by hand here and the fetcher leaves them alone.

When editing a fetched skill, remember the next `mise run skills-update` will
overwrite it — upstream the change or move the skill out of the manifest.

Because skills are vendored, licensing is this repository's problem. Adding an
entry to `upstream-skills.txt` means checking its upstream license and updating
the "Licensing" section of `README.md` plus `LICENSE`. Most skills are MIT;
`agent-browser` and `frontend-design` are Apache 2.0 (`APACHE-LICENSE`). If an
Apache-licensed upstream ever ships a `NOTICE`, its contents must be merged
into a root `NOTICE`.

## Guidelines

**Code quality:**
- Full type annotations (basedpyright: 0 errors)
- Tests for all functionality
- ruff for linting and formatting

## Commit Message Convention

Follow [Conventional Commits](https://conventionalcommits.org/):

**Format:** `type(scope): description`

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `perf`, `revert`, `improvement`, `chore`

## Session Completion

Work is NOT complete until every change is committed, pushed, and CI passes.

1. **Quality gates** (if code changed):
   ```bash
   mise run ci
   ```

2. **Commit**: stage and commit every change from this session. Do not leave the working tree dirty.
   ```bash
   git status              # review untracked and unstaged files
   git add <files>
   git commit -m "<type>(<scope>): <description>"
   ```

3. **Push**:
   ```bash
   git pull --rebase && git push
   git status  # must show "up to date with origin"
   ```

4. **Verify CI**:
   ```bash
   mise run ci-watch
   ```
   On failure, inspect with `gh run view --log-failed`, fix, commit, push, and re-watch.

Never stop before CI is green. If anything fails, resolve and retry.
