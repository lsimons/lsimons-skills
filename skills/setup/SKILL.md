---
name: setup
description: create or improve project scaffolding and boilerplate, setting up metadata files including readme and license, basic agent instructions, dependency management and CI/CD, based on templates
model: opus
---

Bring the scaffolding and boilerplate for this project up to a high standard. The outcome should be a project that is easy to work with for both humans and agents, with clear instructions and useful checks and quality gates.

This skill is meant to be run repeatedly on the same project. The two cases it optimises for are **"some setup was done, more is needed"** and **"setup was done a while ago and the boilerplate has not kept up with industry standards"**. Explore first, work out what is left, then do that.

At least take care of each of the sections below.

## Exploration

Read the repo and form a plan before changing anything. The sections below interact: whether mise is in use informs the README, CI templates and verification commands; monorepo presence informs dependabot `directories` and CI shape; git remote informs issue tracker, labels and security policy.

Look at:

* `git log -10 --oneline`, `ls` — age of the project, whether it is close to empty.
* **Which git host**, unless there are explicit instructions. From `git remote get-url origin`:
   * URL contains `github` -> use GitHub and its `gh` CLI
   * URL contains `gitlab` -> use Gitlab and its `glab` CLI
   * Neither -> fall back to plain `git`
   * No git repo or no git remote -> create a repo with `git init`. Do this immediately. Plain git for now.
* Which metadata files already exist:
   * `LICENSE*`
   * `CODE_OF_CONDUCT.md`
   * `CONTRIBUTING.md`
   * `SECURITY.md`
   * `README.md`
   * `AGENTS.md`
   * `CLAUDE.md`
   * `.gitignore`
   * `.mise.toml` / `mise.toml` / `mise.lock`
   * `.github/workflows/` / `.github/dependabot.yml` / `.gitlab-ci.yml`
   * `docs/agents/issue-tracker.md` / `docs/agents/*`.
   * Read all the files.
   * Determine whether the files still match the project: see *Presence and currency* below.
* **Monorepo signals**:
   * `pnpm-workspace.yaml`,
   * `workspaces` field in `package.json`,
   * `tool.uv.workspace` table in `pyproject.toml`,
   * a populated `packages/*` with its own sources.
   * Absence means single-package, which is almost every repo.
* **Language and toolchain signals**:
   * which language
   * which package manager
   * which test runner.
   * These inform the mise template, the CI template, and the dependabot ecosystems.
* **Prose-project signals**: `.md` files heavily outnumber source files, documents cross-reference each other by heading anchor, no test framework, no build anyone consumes. If this is what the repo is, follow [prose-projects.md](./references/prose-projects.md) and skip *Unit tests* entirely. Do not mistake it for a documentation *site*, which has a build and dependencies.
* **How many remotes**: `git remote -v`. More than one genuine push target — a fork that must stay in step, a mirror — needs a `push` task, not a bare `git push`. See [mise.md](./references/mise.md).
* **Which tools are on `PATH`**:
   * `mise`
   * `zizmor`
   * `actionlint`
   * `gh` / `glab`, and whether `gh`/`glab` are authenticated.
   * This decides which checks can run, and which verification results will come back *unverified*.
* **Project setup docs**:
   * additional `.md` files pointed at by `AGENTS.md` / `CLAUDE.md` / `README.md`
   * `openspec/` / `.openspec` directory and any setup / boilerplate / CI designs inside
   * `docs/spec/` / `docs/adr/` and any setup / boilerplate / CI designs inside

Then present the plan: what is present, what is missing, what is stale. Skip sections that exploration showed are done.

Where a section below asks a question, lead with the recommended answer so the user can accept it in a word, and give an explainer only where the choice informs the setup to do.

## Initial starter templates

* If exploration found the project is close to empty, follow [templates.md](./references/templates.md).
* If the project is established, done with this section.

## Prose projects

If exploration found the prose-project signals — the product is the markdown, there is no application and no site — follow [prose-projects.md](./references/prose-projects.md). It covers the three quality gates, their configs, the pull-request question, and where the writing rules live. Otherwise skip this section.

## Mise

* We need `mise` available. Exploration established whether it is on `PATH`.
* If it is not, ask the user whether it can be installed, and how to do so. Options include:
   * User follows https://mise.jdx.dev/getting-started.html themselves
   * Use homebrew to install: `brew install mise`
   * Use script to install: `curl https://mise.run | sh`
* Then, to configure mise for the project, follow [mise.md](./references/mise.md).

## Metadata files

### Presence and currency

Check for each metadata file:

1. **Presence**: does the file exist? If not, create it, starting from the reference and asset named below where the section names one.
2. **Currency**: does what it says still describe this project? A file that names a task that no longer exists, links to a moved file, or describes an architecture the project has outgrown is worse than no file. Improve it.

**Two exceptions, presence only:** `LICENSE` and `CODE_OF_CONDUCT.md`. Legal and social text is not the agent's to rewrite. Create them if absent; otherwise leave them exactly as they are.

### LICENSE

If `LICENSE`, `LICENSE.md` or `LICENSE.txt` exists, leave it alone. Otherwise follow [licensing.md](./references/licensing.md).

### CODE_OF_CONDUCT.md

If `CODE_OF_CONDUCT.md` exists, leave it alone. Otherwise follow [code-of-conduct.md](./references/code-of-conduct.md).

### CONTRIBUTING.md

Follow [contributing.md](./references/contributing.md).

### SECURITY.md

Follow [security.md](./references/security.md).

### Issue tracker

Follow [issue-tracker.md](./references/issue-tracker.md).

### AGENTS.md / CLAUDE.md

`AGENTS.md` is the canonical agent configuration and `CLAUDE.md` is a symlink to it.

#### Symlinking and deduplicating agent files

On windows skip this subsection: do not create, convert, merge, delete or write to `CLAUDE.md`, and do not add or edit the canonical header line. Do create `AGENTS.md` if it is missing. Report this in verification as deferred to the human: "agent-file symlinking skipped on windows". (While windows git has some support for symlinks with `core.symlinks`, this can be flaky and we choose here not to bother the user with such details, and avoid the chance an agent writes a non-symlinked `CLAUDE.md`.)

Given these `AGENTS.md` and `CLAUDE.md` cases:

1. **Correct**: both files exist and `CLAUDE.md` is a symlink that already resolves to `AGENTS.md` (`readlink CLAUDE.md` prints `AGENTS.md`), so there is nothing to do.
2. **Neither file exists**: create `AGENTS.md`, then `ln -s AGENTS.md CLAUDE.md`.
3. **`AGENTS.md` only**: `ln -s AGENTS.md CLAUDE.md`.
4. **`CLAUDE.md` only, and it is a real file**: convert it: `git mv CLAUDE.md AGENTS.md && ln -s AGENTS.md CLAUDE.md && git add -N CLAUDE.md`.
5. **Both exist and `CLAUDE.md` is a real file**: merge in this order: first copy `CLAUDE.md`'s unique content into `AGENTS.md`, then confirm nothing was lost, and only then `git rm CLAUDE.md && ln -s AGENTS.md CLAUDE.md && git add -N CLAUDE.md`.

Then add this line near the top of `AGENTS.md` if it is not already there, verbatim:

> This file (`AGENTS.md`) is the canonical agent configuration. `CLAUDE.md` is a symlink to this file.

#### Creating or updating agent instructions

**`AGENTS.md` earns its place by holding what an agent needs and a human contributor does not.** Anything else belongs in `README.md` (what the project is, the map) or `CONTRIBUTING.md` (the house rules for the work), with `AGENTS.md` linking to it. Two copies of the same rules drift, and the agent file is the copy that stops being read. Before writing, check what `README.md` and `CONTRIBUTING.md` already say and delete the restatements.

Useful prose for an established project, in roughly this order:

1. **The canonical header line**, then one or two sentences on what kind of project this is, pointing at `README.md` and `CONTRIBUTING.md` for the rest. You can repeat the short description from `README.md`, but do not duplicate all of it.
2. **Overrides.** Where this project contradicts the user's global agent config or the obvious default — no pull requests, `mise run push` instead of `git push`, a non-standard branch name. State it as an override and say why, because an unexplained override reads like an error and gets ignored.
3. **Constraints that carry real cost if broken.** Confidentiality, files that must not be edited, credentials. Name the case that actually bites rather than the general policy.
4. **Commands.** The mise tasks that exist — list them with `mise tasks` — with a line on any check whose failure is not self-explanatory, and where each tool's config lives. A config file is where project-specific reality gets recorded, and an agent that does not know it exists will work around a check inline instead.
5. **Tools and tricks.** The non-obvious commands this project actually uses: how to read its archive format, extract its binary documents, capture its sources, regenerate its outputs, and where scratch work goes. Often the highest-value section, and the one that never gets written, because each item is obvious to whoever discovered it.
6. **Where things go.** For each kind of artifact, which directory and which indexes must be updated in the same commit. Cheap to write, and it prevents the most common category of agent mistake.
7. **What is not the agent's call.** The decisions that need the human, and how to hand them over.

Items 5 and 6 do not apply to a fresh project. Leave them out and add them on a later run of this skill, when there is something true to put in them.

#### The `## Agent skills` section

`AGENTS.md` carries a `## Agent skills` section with a fixed set of subsections. **The section and these subsection headings are a convention shared with other tools: keep them, and keep their names.** Adding subsections is fine; renaming, merging or replacing them is not, even when the content would read better folded elsewhere.

* If a git remote is set up:
   ```
   ### Git remote

   Use <github with `gh`/gitlab with `glab`/plain git commands>.
   ```
* If issue tracking is set up:
   ```
   ### Issue tracker

   Use <github/gitlab/local markdown files>. See `docs/agents/issue-tracker.md`.

   ### Triage labels

   Use needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix. See `docs/agents/issue-tracker.md`.
   ```

Add each subsection to the existing `## Agent skills` section, or create that section if it doesn't exist. Where a subsection needs project detail — two push targets, a label that means something specific here — put it in the subsection rather than in a new section of your own.

### README.md

Where there is no README, start from [README-template.md](./assets/README-template.md), but do not invent answers for missing content. If mise is set up, the Development Commands section should list the tasks that actually exist (`mise tasks`); if mise is not set up, replace or delete that section.

Currency for a README is mostly about whether its description still matches the project. Judge which of these applies:

* Almost no content: improve it based on the template.
* An established project with a lot of documentation (a fleshed out `docs/`, or many `.md` / `.html` files elsewhere): update the README from that documentation and link out to it rather than restating it.
* Little documentation but fleshed out source code: describe what the project is and what it does, based on a high-level review of the source.

Then check the README's relative links. Fix broken references by finding the right file, and remove references to files that do not exist.

### .gitignore

It should cover the build, cache and editor directories this project actually produces — not a generic list for a language it only partly uses — and it must **not** ignore dependency lock files (see [dependencies.md](./references/dependencies.md)).

## Unit tests

If the project has source code but no unit tests, set up unit tests. Use the framework the project already depends on; if there is none, use the default for the language:

| Language   | Default test framework |
| ---------- | ---------------------- |
| Python     | `pytest`               |
| TypeScript | `vitest`               |
| Go         | `go test`              |
| Rust       | `cargo test`           |

Add a single simple 'hello world' test and add source code comments that note it should be replaced with real tests. Wire the framework into a `mise run test` task.

### Unit test coverage

If the project has unit tests and a testing tool that supports reporting coverage but no coverage configuration, propose to the user to set up tooling to track unit test coverage.

Lead with the recommendation: measure current coverage, then propose a minimum coverage bar just below it, capped at 90%. Say the number you measured and the number you propose, so the user can accept in a word.

If current test coverage is less than 70%, warn the user that unit test coverage is low, but do not attempt to improve coverage as part of this setup task.

## Dependency management

Follow [dependencies.md](./references/dependencies.md).

## Continuous integration

Follow [ci.md](./references/ci.md).

## Verification

Follow [verification.md](./references/verification.md).

## Session completion

After sharing the verification report, if no changes were made, we're done. Confirm "No changes made" to the user. Otherwise, confirm with the user whether changes should be committed and pushed. If it is available, use the `/complete` skill for this.
