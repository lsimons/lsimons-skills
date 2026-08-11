# Agent Instructions for lsimons-skills

> This file (`AGENTS.md`) is the canonical agent configuration. `CLAUDE.md` is a symlink to this file.

My agent skills. Every skill is committed here — under `skills/` when it is
enabled and `disabled/` when it is not — whether hand-written or fetched with
[skills.sh](https://www.skills.sh).

Wiring skills into a particular coding agent's configuration (symlinking
into `~/.claude/skills`, `~/.agents/skills`, and friends) is the job of
whatever consumes this repository.

## Quick Reference

Every repo task lives in `.mise.toml`; `mise tasks` lists them.

| Task                     | What it does                                             |
| ------------------------ | -------------------------------------------------------- |
| `mise install`           | Install the pinned toolchain (one-time)                  |
| `mise run install`       | `uv sync --all-groups`                                   |
| `mise run lint`          | `ruff check` + `ruff format --check` + `actionlint`      |
| `mise run format`        | `ruff format` + `ruff check --fix`                       |
| `mise run typecheck`     | `basedpyright` (strict)                                  |
| `mise run test`          | `pytest` with coverage                                   |
| `mise run ci`            | Full gate: lint + typecheck + test                       |
| `mise run audit`         | `zizmor` audit of workflows + dependabot config          |
| `mise run ci-watch`      | Watch GitHub Actions for the current branch              |
| `mise run skills-install`| Fetch only the skills that are missing                   |
| `mise run skills-update` | Re-fetch every skill, replay rewrites, prune strays      |
| `mise run skills-refs`   | Triage worklist of references to renamed skills          |

`audit` is not part of `ci` because it needs network access and a GitHub
token; the workflow's `zizmor` job covers it on every push and PR.

## Structure

```
skills/                   # Skills whose `enabled` flag is true, one per dir
disabled/                 # Skills whose `enabled` flag is false — vendored and
                          # hand-maintained skills alike land here when disabled
scripts/                  # Python tooling that maintains skills/ and disabled/
tests/                    # Tests for scripts/
upstream-skills.toml      # Which skills to fetch, what to call them here, and
                          # which frontmatter fields to override
skill-rewrites.toml       # Cross-reference fixes replayed after each fetch
.mise.toml                # Pinned toolchain + every repo task
pyproject.toml            # ruff, basedpyright, pytest and coverage config
.github/workflows/ci.yml  # CI: mise run lint/typecheck/test + zizmor audit
.github/dependabot.yml    # Weekly uv + github-actions updates, 7-day cooldown
```

There is no installable Python package (`tool.uv.package = false`) —
`scripts` is imported directly via `pythonpath = ["."]` in pytest config,
so run the tooling as a module from the repository root:
`uv run python -m scripts.update_skills`.

## Skills

Everything under `skills/` and `disabled/` is committed, including skills
fetched from skills.sh. `upstream-skills.toml` declares what is fetched;
skills listed under `local` there are maintained by hand and the fetcher
leaves them alone. Read that list from the manifest rather than from here —
it changes. Anything in *either* directory that the manifest does not declare
is reported on every run, and `--prune` deletes it (`prune_skills` scans both,
see `scripts/update_skills.py`).

Every skill also has an `enabled` flag, defaulting to `false`: enabled skills
live at `skills/<name>`, everything else at `disabled/<name>`. Set it
with `[source.enabled]` on a `[[source]]` (keyed by upstream name) or with
`[local-enabled]` at the top level (keyed by local name) — see the comment
block at the top of `upstream-skills.toml`. `mise run skills-update` (via
`sync_skill_locations` in `scripts/update_skills.py`) moves a skill's
directory to match its `enabled` state every run; never `mv` one by hand.

`auto` is the enabled router: it dispatches by intent to the phase skills
(`setup`, `research`, `spike`, `spec`, `build`, `review`, `complete`, `flow`,
`triage`, `bump`), which is why `upstream-skills.toml` declares them as a set.
`leo-bot` is the older cross-pack router — OpenSpec first when the repo has an
`openspec/` directory, then `sbp-*` for mission-critical work, then exactly
one of `mp-*` / `ao-*` / `s-*`. It is currently disabled. When a vendored
skill is added, renamed, or dropped, a router's routing table needs updating
too.

When editing a fetched skill, remember the next `mise run skills-update` will
overwrite it — upstream the change, move the skill out of the manifest, or
express it as a rule in `skill-rewrites.toml`.

### Prefixes and renaming

Skill names are a flat global namespace and packs collide, so each source
declares a `prefix` and every skill from it is vendored under that prefix
(`interview-me` becomes `ao-interview-me`). A name that already carries the
prefix keeps it, so `sbp-*` and `memex-search` are untouched. Current
prefixes: `ao-` (Addy Osmani), `mp-` (Matt Pocock), `s-` (superpowers),
`sbp-` (Schuberg Philis), `memex-`, `vercel-`, `an-` (Anthropic).

`mise run skills-update` handles the mechanical half by itself: it fetches
each skill, installs it under its local name, and rewrites the `name:`
frontmatter field to match. **Renaming skills is not otherwise a job to do by
hand — drive it through the workflow below.**

### Frontmatter overrides

A `[source.frontmatter]` table in `upstream-skills.toml`, keyed by upstream
skill name, sets fields in a fetched skill's YAML header after the fetch:

```toml
[source.frontmatter]
using-agent-skills = { disable-model-invocation = true }
```

It exists for `disable-model-invocation`, which decides whether an agent can
fire a skill by itself or only a human typing its name can. The criterion is
`mp-writing-for-agents/SKILL-MECHANICS.md` — under `skills/` or `disabled/`
depending on that skill's own `enabled` flag, as above: model-invocation is for
skills the agent must reach on its own, or that another skill must reach.
A model-invoked skill's `description` is loaded into every session's context
forever, so the flag is also how context is reclaimed. Only Matt Pocock's pack
sets it upstream; every other pack ships everything model-invocable, and the
overrides here are our own judgement about routers (`using-agent-skills`,
`using-superpowers`, `find-skills` — their targets carry descriptions of their
own) and about blast radius (`autonomous-plan-execution` runs a whole plan
hands-off).

This is structured data, so it does not belong in `skill-rewrites.toml` —
that file is for prose. `name:` cannot be overridden; the fetcher owns it.
Values are strings or booleans, and a field whose value spans multiple lines
is refused rather than mangled. A test asserts the committed `skills/` tree
matches every declared override, so declaring one without re-fetching fails
CI.

### Workflow: adding or re-prefixing a source

The tooling deliberately stops where judgement starts. Cross-references
between skills are prose, and many upstream names are also ordinary words
(`research`, `implement`, `terraform`, `brainstorming`, `triage`), so no
find-and-replace can distinguish "the `research` skill" from "do some
research". That triage is the agent's job.

1. Add or edit the `[[source]]` block in `upstream-skills.toml`. Record its
   `license` and `copyright` — vendoring makes licensing our problem.
2. Run `mise run skills-update`. It fetches, renames, replays
   `skill-rewrites.toml`, then prints two things worth reading:
   - **stale rewrite rules** — a rule whose `old` text no longer appears.
     Upstream moved, or the rule is redundant because a longer rule already
     consumed the text. Fix or delete it; a stale rule fails the run.
   - **the reference report** — every surviving whole-word mention of a
     renamed skill's upstream name. It over-reports on purpose.
3. Triage that report (`mise run skills-refs` re-prints it in full, one line
   per hit, without re-fetching). For each line decide: does this string mean
   the skill, or the word?
   - Skill reference → add a pair to `skill-rewrites.toml`.
   - Ordinary prose → leave it. Most of the report is this.
   - Ambiguous upstream name (flagged `AMBIGUOUS`, e.g.
     `test-driven-development` ships from two packs) → resolve it by the pack
     the *referencing* skill belongs to.
4. Prefer the narrowest `old` string that still catches every real hit:
   `` `interview-me` `` rather than `interview-me`, unless the file is a pure
   routing skill where every mention is a pointer. Pairs apply in the order
   listed, longest first, so `superpowers:writing-plans` fires before
   `writing-plans`.
5. Re-run `mise run skills-update` and confirm zero stale rules. Rules are
   replayed against freshly fetched upstream text, so this is the only way to
   check them — do not apply rules to an already-rewritten working copy.
6. Update the licensing table in `README.md` and, for MIT sources, `LICENSE`.
7. `mise run ci`, then commit `skills/`, both TOML files, and the docs
   together.

### Licensing

Because skills are vendored, licensing is this repository's problem. Every
`[[source]]` records its `license` and `copyright`, and a test enforces that;
those values must also reach the "Licensing" section of `README.md`, and — for
MIT sources — the copyright line in `LICENSE`. Most skills are MIT;
`vercel-agent-browser`, `an-frontend-design` and the sbp-skills set are
Apache 2.0 (`APACHE-LICENSE`). If an Apache-licensed upstream ships a `NOTICE`
with content that applies to what we vendor, that content must be merged into
a root `NOTICE`. sbp-skills ships one, but it covers only `sbp-brandbook`,
which we do not vendor — so no root `NOTICE` is needed.

Not every upstream skill is vendorable. `sbp-brandbook` is proprietary
Schuberg Philis content that forbids redistribution outside its own
repository, so it stays out of the manifest — see the "Not vendored" section
of `README.md`.

## Guidelines

**Code quality:**

- Full type annotations; `basedpyright` strict must report 0 errors.
- Tests for all functionality; the coverage floor is 80%
  (`--cov-fail-under=80` in `pyproject.toml`, enforced by `mise run test`).
- `ruff` for linting and formatting; do not hand-format around it. It is
  configured to skip `skills/` and `disabled/`, which are vendored
  upstream content — do not reformat other people's skills.
- Do not silence a check without a written justification on the same
  line — a bare `# noqa` or `# type: ignore` is not acceptable, a
  narrow `# type: ignore[reportUnknownMemberType]  # <lib> ships no
  stubs` is. Prefer fixing the cause; suppress when the cause is
  outside this repo.
- Never weaken a control to make a check pass: do not lower the
  coverage floor, unpin an action, or delete a failing test.

**Supply chain:**

- `uv.lock` is committed and must stay in the tree.
- GitHub Actions are pinned to full-length commit SHAs with a `# vX.Y.Z`
  comment, and `zizmor` enforces that in CI.
- Every tool in `.mise.toml` is pinned to an exact version, python
  included. Nothing here is covered by dependabot, so refresh it
  deliberately with `mise up` and read the diff.
- The `zizmor` version in `.mise.toml` and the `version:` in the
  workflow's zizmor job must match; bump them together.
- Vendoring skills makes their licensing this repository's problem —
  see "Licensing" above.

## Commit Message Convention

Follow [Conventional Commits](https://conventionalcommits.org/):

**Format:** `type(scope): description`

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `perf`, `revert`, `improvement`, `chore`

## Session Completion

Use `/complete`, available at [skills/complete/SKILL.md](./skills/complete/SKILL.md).
