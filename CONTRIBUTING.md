Thank you for investing your time in contributing to our project!

Any contributions you make are governed by our [License](LICENSE).

Please follow our [Code of Conduct](CODE_OF_CONDUCT.md) to keep our community approachable and respectable.

You could read the [GitHub Docs Contributing Guide](https://github.com/github/docs/blob/main/CONTRIBUTING.md) for general advice on how to contribute.

## Getting set up

```bash
mise install       # install the pinned toolchain
mise run install   # install project dependencies
mise run ci        # lint + typecheck + test — must pass before you open a PR
```

`mise tasks` lists everything else. [AGENTS.md](AGENTS.md) carries the
working agreements in full, including the workflow for adding or
re-prefixing an upstream skill source.

## Filing an issue

Issues are GitHub issues. The labels and the triage flow are documented in
[docs/agents/issue-tracker.md](docs/agents/issue-tracker.md) — new issues get
`needs-triage`. Found a security problem instead? Do not open a public issue;
follow [SECURITY.md](SECURITY.md).

## Before you open a pull request

- Most skills, in **both** `skills/` and `disabled/`, are **vendored**
  upstream content. Editing one directly does not stick — the next
  `mise run skills-update` overwrites it. Upstream the change, or express it
  as a rule in `skill-rewrites.toml`.

  The exception is the skills declared under `local` in
  `upstream-skills.toml`: those are hand-maintained here, never fetched and
  never pruned, and are the ones to edit in place. Check the manifest, not
  the directory — `enabled` decides only *which* of the two directories a
  skill sits in, and says nothing about whether it is vendored.
- Vendoring an upstream makes its licensing this repository's problem: record
  `license` and `copyright` on the `[[source]]`, and mirror them into the
  Licensing table in [README.md](README.md).
- Commit messages follow [Conventional Commits](https://conventionalcommits.org/):
  `type(scope): description`.

Since this is a small hobby project, your contribution may not be noticed for a while if we are busy elsewhere. Sorry!
