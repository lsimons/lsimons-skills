# How to verify a setup run

## Verification is a re-check, not a summary

Re-run every section's own check question against the repo and report what the repo says now. Do not describe what you did from memory.

Recall drifts: a section skipped mid-run quietly vanishes from a remembered summary, and the summary reads clean. A re-derived report cannot flatter itself — and the resulting table *is* the answer to "what setup is still needed", which is what makes running this skill again useful.

Report as a table:

| Section | Before | After | Left to the human |
| ------- | ------ | ----- | ----------------- |

These rows, in this order — including the sections that were already done and the ones that were skipped, which are the rows that tell the user what is left:

starter templates, mise, `LICENSE`, `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `SECURITY.md`, issue tracker, `AGENTS.md` / `CLAUDE.md`, `README.md`, `.gitignore`, unit tests, coverage, dependency management, CI.

## Three kinds of check

They fail differently, so name them differently.

**Syntactic — did I write valid files?** The characteristic failure of a template-driven skill is an unfilled placeholder. Check it precisely: extract the placeholder tokens the template itself declares, then assert none of them survive in the file that was written.

```bash
# tokens the template declares
grep -ohE '<[^>]{1,30}>' skills/setup/assets/README-template.md | sort -u
# -> <how to use the project> <medium description> <Name> <other sections>
#    <pointers at docs/> <project> <short description>
# then assert each of those is absent from README.md
```

A bare `grep '<'` is the wrong check — it false-positives on ordinary prose and on the comments inside the mise templates.

**Behavioural — does it run?** `mise run ci`, plus the tool checks below.

**Standard — does the repo now meet the bar this skill claims?** Pinned actions, committed lock files, a dependency checker, a security audit. This is the class that matters for the "standards moved" case.

## The checks

Most of these check *what is on disk*. Prefer those: anything this run created is still untracked at this point, because the commit is the last step and has not happened yet, so a check that reads the git index answers nothing about a file that was just written.

**Never run `git add -A` to make a check answerable.** It rewrites the user's index, and `/setup` runs on working projects where a partially staged change is normal — `/complete` would then commit more than the user chose. Where the index genuinely has to know about a new path, use `git add -N <path>` (intent-to-add): it records the path and stages no content.

```bash
# workflows + dependabot config + pre-commit config, in one pass.
# --strict-collection turns schema errors into failures instead of warnings.
# The token enables the online audits (impostor-commit, known-vulnerable-actions).
# Without one zizmor warns and falls back to offline: that is an *unverified*
# result for those audits, not a pass. Do not pass --offline to silence it.
GH_TOKEN=$(gh auth token 2>/dev/null) zizmor --collect=all --strict-collection .

# GitLab: server-side validation, resolves include: and project context
glab ci lint

# on disk: the symlink points the right way. No git involved, so this always answers.
test -L CLAUDE.md            # must succeed
readlink CLAUDE.md           # must print AGENTS.md

# on disk: the other half of the same invariant — the canonical header line
grep -F 'This file (`AGENTS.md`) is the canonical agent configuration' AGENTS.md

# lock files must not be ignored. Works on untracked paths, so this always answers.
# PASS = exit 1 with no output. Any line printed names an ignored lock file and is the failure.
git check-ignore -v uv.lock pnpm-lock.yaml go.sum Cargo.lock

# ...and must be tracked. Only answers for a lock file that was already tracked;
# for one created during this run, the check-ignore result above plus its
# presence on disk is the answer, and it becomes tracked at commit time.
git ls-files --error-unmatch uv.lock                            # must succeed

# CLAUDE.md must be recorded as a symlink, not a copy — this catches a later
# agent replacing the link with a text file. `test -L` above already covers the
# on-disk case; run this one only when CLAUDE.md was already tracked, or after
# `git add -N CLAUDE.md` for one created during this run.
git ls-files -s CLAUDE.md    # mode must be 120000

# labels really exist on the remote
gh label list --json name --jq '.[].name'   # diff against the table in issue-tracker.md

# docs must not name tasks that do not exist
mise tasks --json    # every task named in README.md / AGENTS.md must appear here

# unpinned actions, when zizmor is unavailable (zizmor's unpinned-uses is better).
# PASS = no output, and the pipeline exits non-zero because the second grep matched nothing.
grep -nE '^\s*uses:' .github/workflows/*.yml | grep -vE '@[0-9a-f]{40}\s*(#.*)?$'

# did I write what I meant to, and only that?
git status --short
```

Two of these signal success by an empty result and a non-zero exit. Read the output, not the exit code: for `git check-ignore` and for the `uses:` grep, silence is the pass.

The `mise tasks` cross-check is the highest-value cheap check here. It is what keeps `README.md` and `AGENTS.md` honest as `.mise.toml` evolves, and that drift is exactly what the "setup was done a while ago" case is made of.

Two more, by hand:

* Resolve every relative link in `README.md` and in `AGENTS.md`. A link to a file that does not exist is a defect.
* Confirm the coverage floor is actually wired into the test command, rather than merely written down in a config file nothing reads.

## Three outcomes per check, not two

Every check reports **verified**, **unverified**, or **deferred to the human**.

* **verified** — the check ran and passed.
* **unverified** — the check could not run: no `gh` auth, offline, `actionlint` not installed, zizmor's online audits skipped for want of a token. Report it as unverified. Silent green is what makes a verification pass worthless.
* **deferred** — genuinely not an agent's call. Is the code-of-conduct contact a real address? Is the license the right one for this project? Is the coverage floor meaningful? Listing these *is* verification: it prevents false confidence, and it produces the human's to-do list.

## When a check fails

**Loop shape.** Run all the checks → classify each failure → fix only class 1 → re-check once → stop. Terminate when the failing set stops shrinking, not on a counter. Cap at two attempts per item: the first fix addresses the obvious cause, and past the second you are in unknown-unknowns, where more attempts produce thrash rather than progress.

**Three failure classes:**

1. **My write was wrong** — malformed YAML, an unfilled placeholder, the symlink pointing backwards, a documented task that does not exist. Fix it and re-check. This is the only class that may loop.
2. **The repo does not meet the standard for pre-existing reasons** — eight existing workflows with unpinned actions, a lock file gitignored years ago, no tests at all. Report it; leave it alone. On the "standards moved" case this will often be the majority of findings, and whether a `/setup` run expands into a remediation project is the user's call.
3. **The check could not run.** Mark it unverified and move on.

**The rule that matters most:**

> Never repair a check by weakening the standard. Do not lower the coverage floor, add a suppression comment (`# zizmor: ignore`, `# noqa`), un-pin an action, delete the artifact that fails the check, or edit the check itself. If a check cannot pass honestly within two attempts, stop and report the tool's actual error text.

**Loop only on mechanically checkable things.** README quality and `AGENTS.md` content have no oracle, so re-working them on a second pass is stylistic churn that makes the diff worse without making the repo better. Judge them once and move on.

## Running the pass in a subagent

If you can dispatch a subagent, run this verification pass in one; otherwise run the checks inline. Subagent dispatch is not available in every agent runtime.

The reason to prefer the subagent is epistemic, not context economy: the main agent knows what it *intended*, and intent biases it toward seeing success. A subagent given only this checklist, the repo, and the list of touched files has no memory to be motivated by.

Three constraints:

* **Read-only.** Give it shell and file reads, no edits. If the verifier can fix things, the bias has simply moved. Enforce this with the tools it is given, not with an instruction in its prompt.
* **Pass it the list of files this run touched** (`git status --short` is a good start). Without that list it cannot tell class 1 from class 2. Ask it to label each finding with its class.
* **One verifier, sequential.** Do not fan the individual checks out across parallel subagents; a dozen shell one-liners does not justify the orchestration.

Do not use subagents for the writing phase either. Fifteen files with interacting decisions want one coherent context.
