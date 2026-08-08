# lsimons-skills

A collection of agent skills: Markdown skill definitions under
`skills/`, backed by Python scripts under `skills/scripts/`.

## Getting Started

```bash
mise install          # pin + install python + uv
mise run install      # install project deps
mise run test         # run the test suite
```

## Included Configuration

- **Python 3.14+** required
- **ruff** for linting and formatting (line-length: 100)
- **basedpyright** strict mode for type checking
- **pytest** with 80% coverage requirement
- **GitHub Actions CI** on push/PR to main, with actions pinned to
  full-length commit SHAs (the repo setting *Require actions to be
  pinned to a full-length commit SHA* is enabled)
- **`.mise.toml`** pins toolchain + defines every repo task

## Project Structure

```
lsimons-skills/
├── .github/workflows/ci.yml  # CI pipeline (mise-action)
├── .mise.toml                # Toolchain pin + task runner
├── docs/spec/                # Feature specifications
├── skills/                   # Skill definitions (Markdown)
│   └── scripts/              # Python scripts backing the skills
├── tests/                    # Tests for skills/scripts/*.py
├── AGENTS.md                 # AI agent instructions
├── CLAUDE.md -> AGENTS.md    # Claude Code compatibility
├── pyproject.toml            # Project configuration
└── README.md
```

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

See [LICENSE.md](./LICENSE.md).

## Contributing

See [CONTRIBUTING.md](./CONTRIBUTING.md).
