# lsimons-skills

The single source of truth for my agent skills. Every skill lives under
`skills/` and is committed here, whether hand-written or fetched from
[skills.sh](https://www.skills.sh).

This repository only *maintains* `skills/`. Wiring it into a particular
coding agent's configuration (symlinking into `~/.claude/skills`,
`~/.agents/skills`, and friends) is the job of whatever consumes this
repository — for me, the `lsimons-dotfiles` agent topics.

## Layout

```
skills/               # Skill definitions, one directory per skill
scripts/              # Python tooling that maintains skills/
tests/                # Tests for scripts/
upstream-skills.txt   # Manifest of skills fetched from skills.sh
```

## Skills

Skills listed in [`upstream-skills.txt`](./upstream-skills.txt) are fetched
with the skills.sh CLI; everything else under `skills/` (`1password`,
`claude-history`, `python-knowledge-patch`) is maintained by hand and the
fetcher leaves it alone.

Unlike the older dotfiles setup, fetched skills are **vendored in git**, so
re-fetching an upstream skill lands as a reviewable diff.

Add a skill by appending `<repository-url> <skill-name>` to
`upstream-skills.txt` and fetching it:

```bash
mise run skills-install    # fetch only what is missing
mise run skills-update     # re-fetch everything
```

Both accept `--dry-run` when invoked directly:

```bash
uv run python -m scripts.update_skills --dry-run --update
```

Browse and search the catalog with the CLI (`skills find`, `skills list`);
the `find-skills` skill lets agents do that on their own.

## Development Commands

```bash
mise install          # one-time: pin + install toolchain
mise run install      # install project deps
mise run test         # pytest
mise run lint         # ruff check + format --check
mise run typecheck    # basedpyright
mise run format       # ruff format + --fix
mise run ci           # full CI gate
```

## License

See [LICENSE](./LICENSE).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
