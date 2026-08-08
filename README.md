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
skills/                # Skill definitions, one directory per skill
scripts/               # Python tooling that maintains skills/
tests/                 # Tests for scripts/
upstream-skills.toml   # Which skills to fetch, and what to call them here
skill-rewrites.toml    # Cross-reference fixes replayed after each fetch
```

## Skills

Skills declared in [`upstream-skills.toml`](./upstream-skills.toml) are
fetched with the skills.sh CLI. Skills listed there under `local`
(`1password`, `claude-history`, `python-knowledge-patch`) are maintained by
hand and the fetcher leaves them alone.

```bash
mise run skills-install    # fetch only what is missing
mise run skills-update     # re-fetch everything, replay rewrites, prune strays
mise run skills-refs       # list references to renamed skills' upstream names
```

`skills-update` accepts `--dry-run` when invoked directly:

```bash
uv run python -m scripts.update_skills --dry-run --update
```

Browse and search the catalog with the CLI (`skills find`, `skills list`).

### Prefixes

Skill names are one flat namespace, and packs collide — superpowers and
osmani-agent-skills both ship a `test-driven-development`. So each source
declares a prefix, and every skill it provides is vendored under it:

| Prefix | Source |
| --- | --- |
| `ao-` | Addy Osmani's collection |
| `mp-` | Matt Pocock's collection |
| `s-` | superpowers |
| `sbp-` | Schuberg Philis |
| `memex-` | memex CLI |
| `vercel-` | vercel-labs |
| `an-` | Anthropic |

A name that already carries its prefix keeps it, so `sbp-threat-model` and
`memex-search` are not double-prefixed.

### Adding or re-prefixing a source

`mise run skills-update` does the deterministic half — fetch, rename the
directory, rewrite the `name:` frontmatter field, replay
[`skill-rewrites.toml`](./skill-rewrites.toml). It cannot do the other half:
skills refer to each other in prose, and many upstream names are also
ordinary words (`research`, `implement`, `terraform`, `triage`), so no
find-and-replace can tell "the `research` skill" from "do some research".

So the flow is not a script but a prompt: edit `upstream-skills.toml`, then
ask a coding agent to do the download and the intelligent rename. The
procedure it follows is in [AGENTS.md](./AGENTS.md); the judgement it reaches
is recorded in `skill-rewrites.toml` and replayed deterministically on every
later fetch, so routine updates stay a single command.

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

Skills vendored under `skills/` keep their upstream license. Every
`[[source]]` in `upstream-skills.toml` records its license and copyright; this
table mirrors them.

**Apache License 2.0** — see [APACHE-LICENSE](./APACHE-LICENSE):

| Skills | Upstream | Copyright |
| --- | --- | --- |
| `vercel-agent-browser` | [vercel-labs/agent-browser](https://github.com/vercel-labs/agent-browser) | Copyright 2025 Vercel Inc. |
| `an-frontend-design` | [anthropics/skills](https://github.com/anthropics/skills) | Copyright Anthropic PBC |
| `sbp-*` | [lsimons/sbp-skills](https://github.com/lsimons/sbp-skills) | Copyright Schuberg Philis |

**MIT** — everything else:

| Skills | Upstream | Copyright |
| --- | --- | --- |
| `ao-*` | [lsimons/osmani-agent-skills](https://github.com/lsimons/osmani-agent-skills) | Copyright (c) 2025 Addy Osmani |
| `mp-*` | [lsimons/pocock-skills](https://github.com/lsimons/pocock-skills) | Copyright (c) 2026 Matt Pocock |
| `s-*` | [lsimons/superpowers](https://github.com/lsimons/superpowers) | Copyright (c) 2025 Jesse Vincent |
| `memex-*` | [nicosuave/memex](https://github.com/nicosuave/memex) | Copyright (c) 2026 Nico Ritschel |
| `vercel-find-skills`, `vercel-web-design-guidelines` | [vercel-labs](https://github.com/vercel-labs) | Copyright (c) 2026 Vercel, Inc. |
| `1password`, `claude-history`, `python-knowledge-patch` | hand-maintained here | Copyright (c) 2026 Leo Simons |

Upstream copyright holders are collected in [LICENSE](./LICENSE).

### Not vendored

`sbp-brandbook` from [lsimons/sbp-skills](https://github.com/lsimons/sbp-skills)
is deliberately absent from `upstream-skills.toml`. It is proprietary Schuberg
Philis content under its own license, which forbids redistribution outside that
repository, and it bundles commercially licensed TypeType fonts. Point an agent
at a local sbp-skills checkout if you need it.

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
