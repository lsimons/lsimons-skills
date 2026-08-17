---
name: complete
description: drive a task to completion, handling quality gates, commits, pull requests, merge requests, worktree cleanup
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

### Issue tracker tooling

If `docs/agents/issue-tracker.md` exists, read it and follow its instructions for issue tracking. Otherwise, if the issue tracker to use is not specified, choose:

* If the project is using a GitHub remote, use the GitHub issue tracker.
* If the project is using a GitLab remote, use the GitLab issue tracker.
* If the project isn't using GitHub or GitLab, use checked-in markdown files for issue tracking.

## The process

Usually: commit on a new branch, push, open a PR/MR, wait for it to go green. If the project doesn't use branches/PRs, commit and push straight to main and watch main's CI instead. If the user asked for it, also merge, update local main, and clean up the worktree.

Detailed workflow:

1. **Quality gates**: use the repo's own gate command if documented (e.g. `mise run ci`), else what you detected above. If there is no automated quality gate and you changed code, stop.

2. **Branch**: if using a branch workflow and not on a branch yet:

   ```bash
   git checkout -b <type>/(<issue>-)<slug>
   ```

3. **Commit**: stage and commit every change from this session, don't leave the working tree dirty. Check what's being staged before committing — no blind `git add -A`/`git add .` unless in a private worktree, and make sure nothing that looks like a secret is going in. Mention `Closes #<issue>.` if that is applicable. This should cross-link commit with the issue.

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

5. **PR or MR**:

   * Mention `Closes #<issue>.` if that is applicable. This should cross-link PR/MR with the issue.
   * After first push of a new branch:
      * If using GitHub, use `gh pr create` to make a pull request
         * If needed you can use `gh pr create --help` to discover how this command works
      * If using GitLab, use `glab mr create` to make a merge request
         * If needed you can use `glab mr create --help` to discover how this command works

6. **Verify CI**:

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
   * Go to step 10 (Update issue tracking) unless the instruction is to merge.

7. **Merge**:

   * Github Stack: `gh stack merge <id> --yes --rebase`
   * GitHub PR: `gh pr merge <id> --rebase`
   * GitLab MR: `glab mr merge <id> --rebase`
   * Only merge once CI is green — never on red or still-running CI.

8. **Update local main**:

   * Exit worktree, if any: `ExitWorktree` tool if `EnterWorktree` tool was used, otherwise `git worktree list` + `cd <main-repo-dir>`.
   * Confirm `git branch --show-current` reports `main` and there are no local changes (if there are, you can't pull — report it; don't stash on the main worktree, parallel work may be ongoing).
   * `git pull --ff-only origin main`
   * `git worktree remove <worktree-dir>` if needed.

9. **Verify on-merge CI**: same commands as step 6, against `main`. Always report any failure. If it's clearly caused by your change and easy to fix, restart the workflow.

10. **Update issue tracking**: if there is an issue associated and it is complete (code merged), close it in the issue tracker, if there was no `Closes #<issue>.` comment to do so. If the issue is not fully completed, and you are assigned, unassign yourself. If more work is needed to complete the issue and you know what it is, add a comment about what's needed next. If there are related follow-up tasks, file new issues in the issue tracker.


## Verification

- [ ] Quality gates ran (if code changed) and passed
- [ ] All session changes are committed
- [ ] `git push` succeeded and the remote and local branches are in sync
- [ ] CI has a green result (if CI is available)
- [ ] Merge is clean (if merging)
- [ ] Local main is updated (or report dirty)
- [ ] CI on main has a green result (if CI is available)
- [ ] Issue tracker is updated (if issue tracker was used; a `Closes #NNN.` comment on a commit / PR / MR is often enough)
