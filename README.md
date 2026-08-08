# lsimons-skills

A collection of agent skills: Markdown skill definitions under
`skills/`, backed by Python scripts under `skills/scripts/`.

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
