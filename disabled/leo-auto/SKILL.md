---
name: leo-auto
description: Executes the current task hands-off through commit, push, and CI verification, using whichever CLI (gh, glab, or plain git) matches the remote. Use when the user says "auto", "finish this up", or wants the session driven to a pushed, green-CI state without checking in between steps. Not for planning or choosing what to build — it starts once the code changes are ready or in progress.
disable-model-invocation: true
---

# Leo Auto

Drive a task to done: quality gates pass, everything is committed, it's
pushed, and CI is green. No stopping to ask "should I commit now?" or "should
I push?" — those are the point of invoking this. It does not decide *what* to
build; it finishes a change that's already underway.

Related but different: `ao-autonomous-plan-execution` collapses a multi-task
*plan* into one approval, with a test-first loop and one commit per task.
Reach for that when there's a `tasks/plan.md` to execute. `leo-auto` has no
opinion about plans or tasks — it's the finishing move for whatever you're
already working on, in this repo, right now.

## When to use

- The user says "auto", "ship it", "finish this up", or otherwise wants the
  remaining commit/push/CI-verify steps done without a check-in per step
- Code changes exist (staged, unstaged, or already committed) and the
  remaining work is mechanical: verify, commit, push, watch CI

**When NOT to use:**

- Nothing has been built yet — this isn't a substitute for planning or
  implementation
- The user wants to review the diff or approve the commit message before it
  lands — ask first instead of invoking this
- A whole multi-task plan needs running end-to-end — use
  `ao-autonomous-plan-execution`

## Detect the git host

Before touching remotes, work out which CLI applies — don't assume `gh`:

```bash
git remote get-url origin
```

- URL contains `github` → use the `gh` CLI (`gh pr view`, `gh run list`, etc.)
- URL contains `gitlab` → use the `glab` CLI (`glab mr view`, `glab ci view`,
  etc.)
- Neither (no remote, or a host that's neither) → fall back to plain `git`.
  Skip any step that has no plain-git equivalent (e.g. "watch CI") and say so
  rather than guessing at a host-specific command.

If both `gh` and `glab` are installed, the URL substring decides which one to
use for *this* repo — don't default to whichever happens to be configured.

## The process

Work is not complete until every change is committed, pushed, and CI passes.

1. **Quality gates** (if code changed). Use this repo's own gate command if
   one is documented (e.g. `mise run ci`, `make ci`, a package-manager
   script) — don't invent a substitute.

2. **Commit**: stage and commit every change from this session. Do not leave
   the working tree dirty.

   ```bash
   git status              # review untracked and unstaged files
   git add <files>
   git commit -m "<type>(<scope>): <description>"
   ```

   Never `git add -A` / `git add .` blindly — check what's actually being
   staged, especially anything that could be a secret.

3. **Push**:

   ```bash
   git pull --rebase && git push
   git status  # must show "up to date with origin"
   ```

4. **Verify CI**, using the CLI picked above:

   - GitHub: `gh run list` / `gh run view --log-failed` on failure
   - GitLab: `glab ci view` / `glab ci status` on failure
   - Plain git: no hosted CI to check — say so and stop here

   On failure, inspect the log, fix, commit, push, and re-watch. Never mark
   the task done on red CI.

Never stop before CI is green (or, for plain git, before push is confirmed).
If anything fails, resolve and retry rather than reporting partial success.

## Red flags

- Committing with `git add -A` without having looked at `git status` first
- Reaching for `gh` on a GitLab remote (or vice versa) instead of checking
  the remote URL
- Declaring the task done while CI is still running or red
- Force-pushing or skipping hooks to make a failure go away

## Verification

- [ ] Remote host was checked before picking `gh`/`glab`/plain git
- [ ] Quality gates ran (if code changed) and passed
- [ ] All session changes are committed, nothing left dirty
- [ ] `git push` succeeded and the branch is up to date with origin
- [ ] CI was watched to a green result, or plain-git fallback was stated explicitly
