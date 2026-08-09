---
name: complete
description: Executes the current engineering task hands-off through git commit, push, CI and local cleanup.
disable-model-invocation: true
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

Continue working until the task is complete.

Usually that means all changes are committed on a new branch, the branch is pushed to the origin remote, a PR or MR is made for that branch, and CI reports that PR or MR is green.

If the current project specifies it is not using branches/PRs/MRs, it usually means the commits are pushed on the main branch and CI reports that CI on the main branch is green.

If the user specified it, completing the task may additionally mean that the green PR/MR should be merged, the new main CI is green, the local main checkout is updated, and any associated local git worktree is removed.

Detailed workflow:

1. **Quality gates**: test your changes are good.

   * Use this repo's own gate command if one is documented (like `mise run ci`), or use the commands you discovered.
   * If there is no good automated quality gate, and you changed code, stop.

2. **Branch**: if using a branch workflow and you are not on a branch yet:

   ```bash
   git checkout -b <type>/(<issue>-)<slug>
   ```

3. **Commit**: stage and commit every change from this session. Do not leave the working tree dirty.

   ```bash
   git status
   git add <files>
   git commit -m "<type>(<scope>): <description>"
   ```

   * Check what is being staged.
   * Unless you are in a private worktree, do not blindly use `git add -A` / `git add .`. 
   * Make sure you are not adding or committing anything that could be a secrets.

4. **Push**:

   * First push of a new branch:
      ```bash
      git push -u <remote> <branch-name>
      ```
   * Later pushes: 
      ```bash
      git pull --rebase && git push
      ```
   * If using plain Git / no remote CI is configured, stop here.

5. **Verify CI**:

   * Use the CLI picked above:
       * Repository tool: for example `mise run ci-watch`
       * GitHub:
           ```bash
           gh pr checks --watch
           gh run list
           gh run view <id> --log-failed  # on failure
           ```
       * GitLab:
           ```bash
           glab ci status --wait
           glab ci status   # on failure
           ```
       * Plain git: no hosted CI to check — stop here
   * Sometimes CI may take a moment to start, if no checks/status, sleep a bit, try again.
   * On failure, inspect the log, fix, commit, push, and re-watch.
   * Never mark the task done on red CI.
   * Never stop before CI is green.
   * If anything fails, resolve and retry rather than reporting partial success.
   * Stop here unless the instruction is to merge.

6. **Merge**:

   * Use the CLI picked above:
       * Github Stack: `gh stack merge <id> --yes --rebase`
       * GitHub PR: `gh pr merge <id> --rebase`
       * GitLab MR: `glab mr merge <id> --rebase`

7. **Update local main**:

   * Exit worktree, if any:
       * `ExitWorktree` tool if `EnterWorktree` tool was used
       * `pwd && git worktree list` check otherwise
          * `cd <main-repo-dir>`
   * `git status && git branch --show-current` should report `main`
       * If there are local changes you can't pull local main. Report this.
       * Do not stash any changes on the main worktree, because parallel work may be ongoing.
   * `git pull --ff-only origin main` to get the merged changes locally
   * `git worktree remove <worktree-dir>` if needed

8. **Verify on-merge CI**:

   * Use the CLI picked above:
       * Repository tool: for example `mise run ci-watch`
       * GitHub: `gh run list` / `gh run view --log-failed` on failure
       * GitLab: `glab ci view` / `glab ci status` on failure
   * Always report any CI failures on `main`.
   * If a CI failure on `main` is clearly caused by your changes and is easy to fix, restart the workflow to fix that issue.

## Things not to do

* Do not commit with `git add -A` without having looked at `git status` first
* Do not decide on your own tooling when there are user instructions around tool use
* Do not amend commits, force-pushing to remotes, skipping hooks to avoid failures
* Do not reason that a failure is not your fault and then skip over the failure
* Do not merge when CI is not running, when CI is still running, or when CI is red

## Verification

- [ ] Quality gates ran (if code changed) and passed
- [ ] All session changes are committed
- [ ] `git push` succeeded and the remote and local branches are in sync
- [ ] CI has a green result (if CI is available)
- [ ] Merge is clean (if merging)
- [ ] Local main is updated (or report dirty)
- [ ] CI on main has a green result (if CI is available)
