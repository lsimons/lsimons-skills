# lsimons-skills

My agent skills. Every skill lives under `skills/` and is committed here,
whether hand-written or fetched with [skills.sh](https://www.skills.sh).

Upstream sources include forks of
[sbp](https://github.com/lsimons/sbp-skills),
[osmani](https://github.com/lsimons/osmani-agent-skills),
[pocock](https://github.com/lsimons/pocock-skills), and
[superpowers](https://github.com/lsimons/superpowers).

Wiring skills into a particular coding agent's configuration (symlinking
into `~/.claude/skills`, `~/.agents/skills`, and friends) is the job of
whatever consumes this repository. See
[lsimons-dotfiles/agents](https://github.com/lsimons/lsimons-dotfiles/tree/main/agents)
for an example.

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

Browse and search the catalog with the CLI (`skills find`, `skills list`).

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

## Licensing

Skills vendored under `skills/` keep their upstream license. Everything is
MIT-licensed except the skills listed below.

**Apache License 2.0** — see [APACHE-LICENSE](./APACHE-LICENSE):

| Skill | Upstream | Copyright |
| --- | --- | --- |
| `agent-browser` | [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | Copyright 2025 Vercel Inc. |
| `frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) | ? |
| `mcaf-module`, `review-mcaf`, `sbp-*`, `terraform` | [lsimons/sbp-skills](https://github.com/lsimons/sbp-skills) | Copyright Schuberg Philis |

That upstream ships a `NOTICE`; the parts of it that apply here are recorded
in [NOTICE](./NOTICE).

**MIT** — everything else. Upstream copyright holders are listed in
[LICENSE](./LICENSE).

### Not vendored

`sbp-brandbook` from [lsimons/sbp-skills](https://github.com/lsimons/sbp-skills)
is deliberately absent from `upstream-skills.txt`. It is proprietary Schuberg
Philis content under its own license, which forbids redistribution outside that
repository, and it bundles commercially licensed TypeType fonts. Point an agent
at a local sbp-skills checkout if you need it.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
