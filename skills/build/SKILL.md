---
name: build
description: execute a task, solve an issue, fix a bug
argument-hint: [issue or details]
model: sonnet
---

Your task is to do the work requested, working autonomously, completing the work without asking questions. If you cannot continue without asking a question, say so in a clear message and then stop.

If a number or issue id is provided as an argument, look up the ticket details in the issue tracker. If the issue is unassigned, assign it to yourself.

Unless the project does not use branches, if you are on the main branch, start a new branch.

Unless the project does not use worktrees, if you are not in a worktree, do the work in a new worktree.

Then implement the change / solve the issue / fix the bug.

Finish up, using `/complete` if that skill is available and by committing the work and updating the issue tracker otherwise.
