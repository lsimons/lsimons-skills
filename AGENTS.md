# Agent Instructions for lsimons-skills

> This file (`AGENTS.md`) is the canonical agent configuration. `CLAUDE.md` is a symlink to this file.

My agent skills. Every skill lives under `skills/` and is committed here,
whether hand-written or fetched with [skills.sh](https://www.skills.sh).

Wiring skills into a particular coding agent's configuration (symlinking
into `~/.claude/skills`, `~/.agents/skills`, and friends) is the job of
whatever consumes this repository.

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
- **Triage worklist for renamed skills**: `mise run skills-refs`

## Structure

```
skills/                # Skill definitions, one directory per skill
scripts/               # Python tooling that maintains skills/
tests/                 # Tests for scripts/
upstream-skills.toml   # Which skills to fetch, what to call them here, and
                       # which frontmatter fields to override
skill-rewrites.toml    # Cross-reference fixes replayed after each fetch
```

There is no installable Python package (`tool.uv.package = false`) —
`scripts` is imported directly via `pythonpath = ["."]` in pytest config,
so run the tooling as a module from the repository root:
`uv run python -m scripts.update_skills`.

## Skills

Everything under `skills/` is committed, including skills fetched from
skills.sh. `upstream-skills.toml` declares what is fetched; skills listed
under `local` there (`1password`, `claude-history`, `complete`, `leo-bot`,
`python-knowledge-patch`) are maintained by hand and the fetcher leaves them
alone. Anything under `skills/` that the manifest does not declare is
reported on every run, and `--prune` deletes it.

Every skill also has an `enabled` flag, defaulting to `false`: enabled skills
live at `skills/<name>`, everything else at `disabled/<name>`. Set it
with `[source.enabled]` on a `[[source]]` (keyed by upstream name) or with
`[local-enabled]` at the top level (keyed by local name) — see the comment
block at the top of `upstream-skills.toml`. `mise run skills-update` (via
`sync_skill_locations` in `scripts/update_skills.py`) moves a skill's
directory to match its `enabled` state every run; never `mv` one by hand.

`leo-bot` is the cross-pack router — OpenSpec first when the repo has an
`openspec/` directory, then `sbp-*` for mission-critical work, then exactly
one of `mp-*` / `ao-*` / `s-*`. When a vendored skill is added, renamed, or
dropped, its routing table needs updating too.

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
`skills/mp-writing-for-agents/SKILL-MECHANICS.md`: model-invocation is for
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
- Full type annotations (basedpyright: 0 errors)
- Tests for all functionality
- ruff for linting and formatting

## Commit Message Convention

Follow [Conventional Commits](https://conventionalcommits.org/):

**Format:** `type(scope): description`

**Types:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `build`, `ci`, `perf`, `revert`, `improvement`, `chore`

## Session Completion

Use `/complete`, available at [skills/complete/SKILL.md](./skills/complete/SKILL.md).

# Licensing

When adding an entry to `upstream-skills.txt`, check the upstream license and
update the README, LICENSE, and — for a new Apache-licensed upstream — implement
any `NOTICE` requirement.
