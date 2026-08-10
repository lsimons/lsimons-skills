---
name: complete
description: drive a task to completion
model: sonnet
---

# Complete

Drive an engineering task to done: quality gates pass, everything is committed, it's pushed, and CI is green. The user is hands-off, so no stopping to ask "should I commit now?" or "should I push?".

If the user did not specify it yet, before starting work, ask the user what completed work means:

- PR created and CI is green
- PR merged, local main is updated, worktree cleaned up
- committed and pushed directly on main
- Something else?

## Detect tooling

If there are no explicit instructions, discover what tools to use:

### Git tooling

```bash
git remote get-url origin
```

- URL contains `github` -> use the `gh` CLI
- URL contains `gitlab` -> use the `glab` CLI
- Neither -> fall back to plain `git` and local `mise` tasks
- No git repo or no git remote -> stop, because this skill can't be used

If github:

```bash
gh stack --help || echo no gh stack
```

If `gh stack` is available, use it to manage multiple stacked PRs.

### Quality gate tooling

Look for 'ci' commands/scripts to use:

```bash
mise tasks || echo no mise
uv run || echo no uv
pnpm run || echo no pnpm
npm run || echo no npm
ls scripts || echo no scripts dir
```

## The process

Usually: commit on a new branch, push, open a PR/MR, wait for it to go green. If the project doesn't use branches/PRs, commit and push straight to main and watch main's CI instead. If the user asked for it, also merge, update local main, and clean up the worktree.

Detailed workflow:

1. **Quality gates**: use the repo's own gate command if documented (e.g. `mise run ci`), else what you detected above. If there is no automated quality gate and you changed code, stop.

2. **Branch**: if using a branch workflow and not on a branch yet:

   ```bash
   git checkout -b <type>/(<issue>-)<slug>
   ```

3. **Commit**: stage and commit every change from this session, don't leave the working tree dirty. Check what's being staged before committing — no blind `git add -A`/`git add .` unless in a private worktree, and make sure nothing that looks like a secret is going in. Mention `Closes #<issue>.` if that is applicable.

4. **Push**:

   * First push of a new branch:
      ```bash
      git push -u <remote> <branch-name>
      ```
   * Later pushes:
      ```bash
      git pull --rebase && git push
      ```
   * Plain Git with no remote CI configured: stop here.

5. **Verify CI**:

   * Repository tool: e.g. `mise run ci-watch`
   * GitHub:
       ```bash
       gh pr checks --watch
       gh run view <id> --log-failed  # on failure
       ```
   * GitLab:
       ```bash
       glab ci status --wait
       glab ci status   # on failure
       ```
   * Plain git: no hosted CI to check — stop here.
   * CI can take a moment to start; if there's nothing to watch yet, wait and retry.
   * On failure: inspect the log, fix, commit, push, re-watch. Don't stop before CI is green, and don't rationalize a failure as unrelated to your change.
   * Stop here unless the instruction is to merge.

6. **Merge**:

   * Github Stack: `gh stack merge <id> --yes --rebase`
   * GitHub PR: `gh pr merge <id> --rebase`
   * GitLab MR: `glab mr merge <id> --rebase`
   * Only merge once CI is green — never on red or still-running CI.

7. **Update local main**:

   * Exit worktree, if any: `ExitWorktree` tool if `EnterWorktree` tool was used, otherwise `git worktree list` + `cd <main-repo-dir>`.
   * Confirm `git branch --show-current` reports `main` and there are no local changes (if there are, you can't pull — report it; don't stash on the main worktree, parallel work may be ongoing).
   * `git pull --ff-only origin main`
   * `git worktree remove <worktree-dir>` if needed.

8. **Verify on-merge CI**: same commands as step 5, against `main`. Always report any failure. If it's clearly caused by your change and easy to fix, restart the workflow.

## Verification

- [ ] Quality gates ran (if code changed) and passed
- [ ] All session changes are committed
- [ ] `git push` succeeded and the remote and local branches are in sync
- [ ] CI has a green result (if CI is available)
- [ ] Merge is clean (if merging)
- [ ] Local main is updated (or report dirty)
- [ ] CI on main has a green result (if CI is available)
