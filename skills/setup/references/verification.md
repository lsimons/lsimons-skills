# How to verify a setup run

Verify the work done and report the outcome. Use a subagent if possible (see below).

## Verification is a re-check

Specific check commands are given below. Re-run every section's own check question against the repo and report current state. Do not describe what you did from memory.

## Result table

Compile a table:

| Section | Before | After | Left to the human |
| ------- | ------ | ----- | ----------------- |

These sections, in this order — including the sections that were already done and the ones that were skipped:

* starter templates
* mise
* `LICENSE`
* `CODE_OF_CONDUCT.md`
* `CONTRIBUTING.md`
* `SECURITY.md`
* issue tracker
* `AGENTS.md` / `CLAUDE.md`
* `README.md`
* `.gitignore`
* unit tests
* unit test coverage
* dependency management
* CI

## Three kinds of check

They fail differently, so name them differently.

**Syntactic: did I write valid files?** The characteristic failure is an unfilled placeholder. Check it precisely: extract the placeholder tokens the template itself declares, then assert none of them survive in the file that was written.

For example, for the README, look for placeholder tokens the template declares:

```bash
SKILL_DIR=[skill base directory]
grep -ohE '<[^>]{1,80}>' ${SKILL_DIR}/assets/README-template.md | sort -u
# -> <how to use the project> <medium description> <Name> <other sections>
#    <pointers at docs/> <project> <short description>
```

And then assert each of those is absent from the actual README.md.

A bare `grep '<'` is the wrong check — it false-positives on ordinary prose and on the comments inside the mise templates.

**Behavioural: does it run?** `mise run ci`, plus the tool checks below.

**Standard: does the repo now meet the bar this skill claims?** Pinned actions, committed lock files, a dependency checker, a security audit.

## The checks

Most of these check *what is on disk*. Prefer those: anything this run created is still untracked at this point, because the commit is the last step and has not happened yet, so a check that reads the git index answers nothing about a file that was just written.

**Never run `git add -A` to make a check answerable.** It rewrites the user's index, and `/setup` runs on working projects where a partially staged change is normal, and we don't want to commit more than the user chose. Where the index genuinely has to know about a new path, use `git add -N <path>` (intent-to-add): it records the path and stages no content.

Checks:

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
test -L CLAUDE.md            # skip on windows; must succeed
readlink CLAUDE.md           # skip on windows; must print AGENTS.md

# skip on windows; on disk: the other half of the same invariant — the canonical header line
grep -F 'This file (`AGENTS.md`) is the canonical agent configuration' AGENTS.md

# lock files must not be ignored. Works on untracked paths, so this always answers.
# PASS = exit 1 with no output. Any line printed names an ignored lock file and is the failure.
git check-ignore -v uv.lock pnpm-lock.yaml go.sum Cargo.lock mise.lock

# ...and must be tracked. Only answers for a lock file that was already tracked;
# for one created during this run, the check-ignore result above plus its
# presence on disk is the answer, and it becomes tracked at commit time.
git ls-files --error-unmatch uv.lock                            # must succeed

# CLAUDE.md must be recorded as a symlink, not a copy — this catches a later
# agent replacing the link with a text file. `test -L` above already covers the
# on-disk case; run this one only when CLAUDE.md was already tracked, or after
# `git add -N CLAUDE.md` for one created during this run.
git ls-files -s CLAUDE.md    # skip on windows; mode must be 120000

# labels really exist on the remote
gh label list --json name --jq '.[].name'      # diff against the table in issue-tracker.md
glab label list --output json --jq '.[].name'  # for gitlab instead of github

# docs must not name tasks that do not exist
mise tasks --json    # every task named in README.md / AGENTS.md must appear here

# unpinned actions, when zizmor is unavailable (zizmor's unpinned-uses is better).
# PASS = no output, and the pipeline exits non-zero because the second grep matched nothing.
grep -nE '^\s*uses:' .github/workflows/*.yml | grep -vE '@[0-9a-f]{40}\s*(#.*)?$'

# did I write what I meant to, and only that?
git status --short
```

Two of these signal success by an empty result and a non-zero exit. Read the output, not the exit code: for `git check-ignore` and for the `uses:` grep, silence is the pass.

Two more, by hand:

* Resolve every relative link in `README.md` and in `AGENTS.md`. A link to a file that does not exist is a defect.
* Confirm the coverage floor is actually wired into the test command, rather than merely written down in a config file nothing reads.

## Three outcomes per check, not two

Every check reports **verified**, **unverified**, or **deferred to the human**.

* **verified**: the check ran and passed.
* **unverified**: the check could not run: no `gh` auth, offline, `actionlint` not installed, zizmor's online audits skipped for want of a token.
* **deferred**: not an agent's call. Is the code-of-conduct contact a real address? Is the license the right one for this project? Is the coverage floor meaningful? Listing these *is* verification: it prevents false confidence, and it produces the human's to-do list.

## When a check fails

Re-check for failures:

* Run all the checks once
* Classify each failure (see below)
* Fix only class 1 errors
* Re-check once
* Stop.

If your first attempt and your attempted fix did not work then you risk producing trash rather than progress, so don't keep looping.

Three failure classes:

1. **My write was wrong**: malformed YAML, an unfilled placeholder, a symlink pointing backwards, a documented task that does not exist. Fix it and re-check.
2. **The repo does not meet the standard for pre-existing reasons**: eight existing workflows with unpinned actions, a lock file gitignored years ago, no tests at all. Report it; leave it alone.
3. **The check could not run**: mark it unverified and move on.

The rule that matters most:

Never repair a check by weakening the standard. Do not lower the coverage floor, add a suppression comment (`# zizmor: ignore`, `# noqa`), un-pin an action, delete the artifact that fails the check, or edit the check itself. If a check cannot pass honestly within two attempts, stop and report the tool's actual error text.

Loop only on mechanically checkable things. Re-working text that you hand-edited (like the README) is stylistic churn that makes the diff worse without making the repo better. Judge once and move on.

## Running verification in a subagent

If you can dispatch subagents, run this verification pass in one, because a subagent is not biased by the main agent's context.

Three subagent constraints:

* **Read-only**: allow it shell and file reads, no edits. If the verifier can fix things, the bias has simply moved. Enforce this with the tools it is given, not with an instruction in its prompt.
* **Modified files only**: tell it to look only at files touched (`git status --short`), so that it can tell class 1 failures from class 2 failures.
* **One sequential verifier**: the verification checks are quick and do not warrant coordination overhead.

Handle any class 1 fixes directly, and then have the subagent re-check the fixes. Do not use a subagent for writing the fixes.

## Report

Report the verification results:

1. The re-check table: **section | before | after | left to the human**.
2. The verified / unverified / deferred lists.
3. Which files the human should expect to hand-edit (the *deferred* list is most of this).
