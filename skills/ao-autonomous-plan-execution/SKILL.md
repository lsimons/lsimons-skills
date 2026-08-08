---
name: ao-autonomous-plan-execution
description: Executes an entire task plan hands-off after a single approval. Use when the user asks to build, implement, or run "the whole plan," "all tasks," or "autonomously" / "auto" once a plan already exists. Not for implementing one task at a time — use ao-incremental-implementation and ao-test-driven-development directly for that.
---

# Autonomous Plan Execution

## Overview

Collapse plan and build into one run: get one approval up front, then execute every task in a plan without the human stepping in between. This removes the manual checkpoint *between* tasks — it does not remove verification. Every task still earns a failing-then-passing test and its own commit, exactly as it would one task at a time.

## When to Use

- A plan already exists (or can be generated) and the user wants it executed end-to-end without approving each task individually
- The user says "build the whole plan," "implement all the tasks," or invokes autonomous/auto mode

**When NOT to use:**

- Implementing just the next task — use `ao-incremental-implementation` and `ao-test-driven-development` directly, one task at a time, no autonomy gate needed
- No spec exists yet — follow `ao-spec-driven-development` first
- The user wants to review and approve each task before it's built

## Preconditions

1. **Require a spec.** Look only for a spec at a known path: `SPEC.md` at the repo root, `docs/SPEC.md`, a file under `spec/`, or — for the numbered-corpus convention — the relevant `docs/spec/SNN-<slug>.md`. A README or arbitrary doc does not count. If none exists, stop and tell the user to run `ao-spec-driven-development` first — do not invent requirements.
2. **Establish a clean baseline.** Run `git status --porcelain`. If there are uncommitted changes outside the expected planning artifacts (`SPEC.md`, `docs/SPEC.md`, `spec/*`, `docs/spec/*`, `tasks/plan.md`, `tasks/todo.md`), stop and ask the user to commit, stash, or confirm how to handle them. Autonomous per-task commits must not absorb unrelated local work, or the clean-rollback guarantee breaks.
3. **Plan if needed.** If there is no `tasks/plan.md`, invoke `ao-planning-and-task-breakdown` to generate one.

## The Process

1. **Single checkpoint.** Present the full plan and wait for an unambiguous affirmative ("approve," "go," "yes"). Treat hedged responses ("looks reasonable," "I guess") as **not** approved. This is the only human gate — after approval, run autonomously. If you generated `tasks/plan.md` in this run, commit it as a single preparatory commit now so it doesn't bleed into the first task's commit.
2. **Execute every task in dependency order.** Use each task's declared dependencies; if they aren't explicit, execute in the order the plan lists them. For each task, run the full test-driven increment loop:
   - Read the task's acceptance criteria
   - Load relevant context (existing code, patterns, types)
   - Write a failing test for the expected behavior (RED)
   - Implement the minimum code to pass the test (GREEN)
   - Run the full test suite to check for regressions
   - Run the build to verify compilation
   - Commit with a descriptive message
   - Mark the task complete in `tasks/todo.md`

   Stage only the files that task touched plus its task-status update — never a blanket add — and make one commit per task so any point is a clean rollback.
3. **Stop and ask the user** (do not push through) when:
   - a test can't be made to pass or the build breaks without an obvious fix → follow `ao-debugging-and-error-recovery`
   - the spec is ambiguous, or a task needs a decision the spec doesn't cover
   - a task is high-risk or irreversible — auth/permission changes, destructive data migrations, payments, deletions, deploys, anything touching secrets, or anything that can't be undone with `git revert` → follow `ao-doubt-driven-development` and get explicit sign-off before continuing

   After the user resolves a blocker, resume from the next pending task.
4. **Summarize at the end:** tasks completed, tests added, commits made, and anything skipped, flagged, or left for the user.

## Common Rationalizations

| Rationalization | Reality |
|---|---|
| "The plan looked fine, I'll skip the explicit approval" | Hedged agreement isn't approval. Ambiguity here means autonomous execution starts on an unconfirmed plan. |
| "I'll batch a few tasks into one commit to save time" | Batching breaks the clean-rollback guarantee — one bad task now takes several good ones down with it. |
| "This migration looks safe enough to just run" | Irreversible operations always need sign-off, regardless of how safe they look. |
| "Tests are slowing down the autonomous run" | Autonomy removes the human checkpoint between tasks, not the verification within each one. |

## Red Flags

- Starting execution without an explicit, unambiguous approval
- More than one task's changes in a single commit
- Continuing past a failing test or broken build without stopping
- Executing a high-risk or irreversible task without pausing for sign-off
- No `tasks/todo.md` update after a task completes

## Verification

- [ ] The plan was approved unambiguously before execution began
- [ ] Every task has its own commit with a passing test suite and clean build
- [ ] `tasks/todo.md` reflects the true completion state
- [ ] Any high-risk or ambiguous task paused for explicit sign-off rather than proceeding
- [ ] The end-of-run summary lists what was built, skipped, and flagged
