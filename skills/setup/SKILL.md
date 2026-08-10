---
name: setup
description: improve project scaffolding and boilerplate
model: opus
---

Bring the scaffolding and boilerplate for this project up to a high standard. The outcome should be a project that is easy to work with for both humans and agents, with clear instructions and useful checks and quality gates. At least take care of each of these sections:

## GitHub, GitLab, or something else

If there are no explicit instructions, discover what git remote to use:

```bash
git remote get-url origin
```

- URL contains `github` -> use GitHub and its `gh` CLI
- URL contains `gitlab` -> use Gitlab and its `glab` CLI
- Neither -> fall back to plain `git`
- No git repo or no git remote -> create a repo with `git init`, plain git for now

## Initial starter templates

* Check if this project is almost empty: `git log -10 --oneline`, `ls`.
* If the project is established, done with this section.
* Otherwise, follow [templates.md](./references/templates.md).

## Mise

* We need mise available.
* Run `command -v mise` to check if Mise is installed.
* If mise is not installed, ask the user whether it can be installed, and how to do so. Options include:
   * User follows https://mise.jdx.dev/getting-started.html themselves
   * Use homebrew to install: `brew install homebrew`
   * Use script to install: `curl https://mise.run | sh`
* Then, to configure mise for the project, follow [mise.md](./references/mise.md).

## Metadata files

### LICENSE

* Check if `LICENSE` or `LICENSE.md` or `LICENSE.txt` exists in the root of the project.
* If a license file exists, done with this section.
* Otherwise, follow [licensing.md](./references/licensing.md).

### CODE_OF_CONDUCT.md

* Check if `CODE_OF_CONDUCT.md` exists in the root of the project.
* If a code of conduct exists, done with this section.
* Otherwise, follow [code-of-conduct.md](./references/code-of-conduct.md).

### CONTRIBUTING.md

* Check if `CONTRIBUTING.md` exists in the root of the project.
* If a contribution guide exists, done with this section.
* Otherwise, follow [contributing.md](./references/contributing.md).

### SECURITY.md

* Check if `SECURITY.md` exists in the root of the project.
* If a security policy exists, done with this section.
* Otherwise, see [security.md](./references/security.md) for more instructions.

### Issue tracker

* Check if `docs/agents/issue-tracker.md` exists.
* If an issue tracker config exists, done with this section.
* Otherwise, see [issue-tracker.md](./references/issue-tracker.md) for more instructions.

### AGENTS.md / CLAUDE.md

* Check if `AGENTS.md` and/or `CLAUDE.md` exist in the root of the project.
* Update the files for accuracy, clarity, and brevity, removing any duplication.

#### Symlinking and deduplicating agent files

* If there is an `AGENTS.md` but no `CLAUDE.md`, add a symlink from `CLAUDE.md` to `AGENTS.md`: `ln -s AGENTS.md CLAUDE.md` in the repo root.
* Otherwise, if there is an `CLAUDE.md` but no `AGENTS.md`, add a symlink from `AGENTS.md` to `CLAUDE.md`: `ln -s CLAUDE.md AGENTS.md` in the repo root.
* If both files exist, intelligently merge their contents into `AGENTS.md`, remove `CLAUDE.md` and replace it with a symlink to `AGENTS.md`.
* The layout of the files should be clear. If they don't mention each other yet, add a line near the top of the file (swap `AGENTS.md` and `CLAUDE.md` if that is correct):

   > This file (`AGENTS.md`) is the canonical agent configuration. `CLAUDE.md` is a symlink to this file.

#### Creating or updating agent instructions

* If there are no such files yet, create a basic `AGENTS.md`, and then a `CLAUDE.md` symlink to it.
* If mise is set up, the `AGENTS.md` should mention the available tasks. List them with `mise tasks`.
* If a git remote is set up, the `AGENTS.md` should mention what is in use, somewhat like this:
   ```
   ### Git remote

   Use <github with `gh`/gitlab with `glab`/plain git commands>.
   ```
   * Add this subsection to an existing `## Agent skills` section, or create that section if it doesn't exist.
* You can repeat the short description from `README.md` in the agent file, but avoid duplicating all of README.md in the agent file.
* If issue tracking is set up, the `AGENTS.md` should summarize the setup and reference the details, somewhat like this:
   ```
   ### Issue tracker

   Use <github/gitlab/local markdown files>. See `docs/agents/issue-tracker.md`.

   ### Triage labels

   Use needs-triage, needs-info, ready-for-agent, ready-for-human, wontfix. See `docs/agents/issue-tracker.md`.
   ```
   * Add these subsections to an existing `## Agent skills` section, or create that section if it doesn't exist.
* Avoid duplicating or conflicting content in the agents file, instead edit it for consistency and brevity.

### README.md

* Check if `README.md` exists in the root of the project.
* If the project has no README.md, write a basic one based on the contents of the project.
   * Use [README-template.md](./assets/README-template.md), but do not invent answers for missing content.
   * If mise is set up, the Development Commands section should mention the available tasks. List them with `mise tasks`. If mise is not set up, replace or delete the section.
* Check the README's relative links. See if you can fix broken references by finding the right file. Remove references to files that do not exist.
* Judge the README's description and whether it needs improvement:
   * If the file exists but has almost no content, improve the contents based on the template.
   * For an established project with a lot of documentation (fleshed out docs/ or many .md or .html files elsewhere), update the README based on the documentation and link it to those docs.
   * If the project does not have much documentation but does have fleshed out source code, improve the README based on a high-level review of the source code: describe what the project is and what it does.

### .gitignore

* Check if `.gitignore` exists in the root of the project.
* If a .gitignore file exists, done with this section.
* Otherwise, write a basic .gitignore file appropriate for this kind of project.

## Unit tests

If the project has source code but no unit tests, set up unit tests using the chosen framework. Add a single simple 'hello world' test and add source code comments that note it should be replaced with real tests.

### Unit test coverage

If the project has unit tests and a testing tool that supports reporting coverage but no coverage configuration, propose to the user to set up tooling to track unit test coverage. Recommend to set the minimum coverage bar to be just below current test coverage, up to a maximum of 90%. If current test coverage is less than 70%, warn the user that unit test coverage is low, but do not attempt to improve coverage as part of this setup task.

## Dependency management

See [dependencies.md](./references/dependencies.md) for instructions.

## Continuous integration

See [ci.md](./references/ci.md) for instructions.

## Verification

Run the discovered or created local ci commands to test the result, for example `mise run ci`.

Report on the major changes made and files changed.

Confirm with the user whether changes should be committed and pushed. If so, use the `/complete` skill.
