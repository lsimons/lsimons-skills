# Agent Instructions for lsimons-skills

> This file (`AGENTS.md`) is the canonical agent configuration. `CLAUDE.md` is a symlink to this file.

A collection of agent skills: Markdown skill definitions plus their supporting Python scripts.

## Quick Reference

- **One-time**: `mise install`
- **Setup**: `mise run install` (or `uv sync --all-groups`)
- **Test**: `mise run test` (or `uv run pytest`)
- **Lint**: `mise run lint` (or `uv run ruff check . && uv run ruff format --check .`)
- **Typecheck**: `mise run typecheck` (or `uv run basedpyright`)
- **Format**: `mise run format` (or `uv run ruff format . && uv run ruff check --fix .`)
- **Full CI gate**: `mise run ci`

## Structure

```
skills/            # Skill definitions (Markdown)
skills/scripts/    # Python scripts backing the skills
tests/             # Tests for skills/scripts/*.py
```

There is no installable Python package (`tool.uv.package = false`) —
`skills/scripts` is imported directly via `pythonpath = ["."]` in
pytest config.

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
