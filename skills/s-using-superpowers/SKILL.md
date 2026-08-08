---
name: s-using-superpowers
description: Discovers and invokes Superpowers skills. Use when starting a task that might match a process skill (design, debugging, planning, review, verification) — this is the meta-skill that governs how the rest of this pack is discovered and invoked.
---

# Using Superpowers

## Overview

Superpowers is a small set of process skills for software development: designing before building, debugging systematically, planning and executing multi-step work, and reviewing before shipping. This meta-skill helps you pick the right one.

## Skill Discovery

```
Task arrives
    │
    ├── Creative/build work (feature, component, new behavior)? → s-brainstorming (first, before any code)
    ├── Bug, test failure, unexpected behavior? ─────────────→ s-systematic-debugging (before proposing fixes)
    ├── Have a spec, need a written plan? ────────────────────→ s-writing-plans
    ├── Executing a plan?
    │   ├── Separate session, review checkpoints? ───────────→ s-executing-plans
    │   └── Independent tasks, current session, subagents available? → s-subagent-driven-development
    ├── 2+ independent tasks, no shared state? ───────────────→ s-dispatching-parallel-agents
    ├── Need an isolated workspace before starting? ──────────→ s-using-git-worktrees
    ├── Implementing any feature or bugfix? ──────────────────→ s-test-driven-development (before writing implementation code)
    ├── About to claim work is done/fixed/passing? ───────────→ s-verification-before-completion (before committing or opening a PR)
    ├── Requesting review of finished work? ───────────────────→ s-requesting-code-review
    ├── Received review feedback? ────────────────────────────→ s-receiving-code-review (before implementing suggestions)
    ├── Implementation complete, tests pass, need to merge? ──→ s-finishing-a-development-branch
    └── Creating or editing a skill? ─────────────────────────→ s-writing-skills
```

## Skill Priority

When more than one skill applies, process skills set the approach before implementation skills carry it out:

- "Let's build X" → `s-brainstorming` first, then whatever implementation skill fits.
- "Fix this bug" → `s-systematic-debugging` first, then domain-specific work.

## Rules

1. Check for an applicable skill before starting non-trivial work — including before clarifying questions, if the question itself is part of a process a skill governs (e.g. s-brainstorming's own questions).
2. Skills are workflows, not suggestions — follow the steps in order, including verification steps.
3. Multiple skills can chain: `s-brainstorming` → `s-writing-plans` → `s-subagent-driven-development` → `s-test-driven-development` → `s-requesting-code-review` → `s-finishing-a-development-branch` is a typical full cycle for a feature.
4. If a skill turns out to be the wrong fit partway through, say so and stop using it rather than forcing the rest of its steps.

## User Instructions

User instructions (CLAUDE.md, AGENTS.md, direct requests) take precedence over skills, which in turn override default behavior.
