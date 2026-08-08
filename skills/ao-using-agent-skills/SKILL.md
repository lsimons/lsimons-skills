---
name: ao-using-agent-skills
description: Discovers and invokes agent skills. Use when starting a session or when you need to discover which skill applies to the current task. This is the meta-skill that governs how all other skills are discovered and invoked.
disable-model-invocation: true
---

# Using Agent Skills

## Overview

Agent Skills is a collection of engineering workflow skills organized by development phase. Each skill encodes a specific process that senior engineers follow. This meta-skill helps you discover and apply the right skill for your current task.

## Skill Discovery

When a task arrives, identify the development phase and apply the corresponding skill:

```
Task arrives
    │
    ├── Don't know what you want yet? ──────→ ao-interview-me
    ├── Have a rough concept, need variants? → ao-idea-refine
    ├── New project/feature/change? ──→ ao-spec-driven-development
    ├── Have a spec, need tasks? ──────→ ao-planning-and-task-breakdown
    ├── Implementing code? ────────────→ ao-incremental-implementation
    │   └── Whole plan, hands-off after one approval? → ao-autonomous-plan-execution
    │   ├── UI work? ─────────────────→ ao-frontend-ui-engineering
    │   ├── API work? ────────────────→ ao-api-and-interface-design
    │   ├── Need better context? ─────→ ao-context-engineering
    │   ├── Need doc-verified code? ───→ ao-source-driven-development
    │   └── Stakes high / unfamiliar code? ──→ ao-doubt-driven-development
    ├── Writing/running tests? ────────→ ao-test-driven-development
    │   └── Browser-based? ───────────→ ao-browser-testing-with-devtools
    ├── Something broke? ──────────────→ ao-debugging-and-error-recovery
    ├── Reviewing code? ───────────────→ ao-code-review-and-quality
    │   ├── Too complex? ─────────────→ ao-code-simplification
    │   ├── Security concerns? ───────→ ao-security-and-hardening
    │   └── Performance concerns? ────→ ao-performance-optimization
    ├── Committing/branching? ─────────→ ao-git-workflow-and-versioning
    ├── CI/CD pipeline work? ──────────→ ao-ci-cd-and-automation
    ├── Deprecating/migrating? ────────→ ao-deprecation-and-migration
    ├── Writing docs/ADRs? ───────────→ ao-documentation-and-adrs
    ├── Adding logs/metrics/alerts? ───→ ao-observability-and-instrumentation
    └── Deploying/launching? ─────────→ ao-shipping-and-launch
```

## Core Operating Behaviors

These behaviors apply at all times, across all skills. They are non-negotiable.

### 1. Surface Assumptions

Before implementing anything non-trivial, explicitly state your assumptions:

```
ASSUMPTIONS I'M MAKING:
1. [assumption about requirements]
2. [assumption about architecture]
3. [assumption about scope]
→ Correct me now or I'll proceed with these.
```

Don't silently fill in ambiguous requirements. The most common failure mode is making wrong assumptions and running with them unchecked. Surface uncertainty early — it's cheaper than rework.

### 2. Manage Confusion Actively

When you encounter inconsistencies, conflicting requirements, or unclear specifications:

1. **STOP.** Do not proceed with a guess.
2. Name the specific confusion.
3. Present the tradeoff or ask the clarifying question.
4. Wait for resolution before continuing.

**Bad:** Silently picking one interpretation and hoping it's right.
**Good:** "I see X in the spec but Y in the existing code. Which takes precedence?"

### 3. Push Back When Warranted

You are not a yes-machine. When an approach has clear problems:

- Point out the issue directly
- Explain the concrete downside (quantify when possible — "this adds ~200ms latency" not "this might be slower")
- Propose an alternative
- Accept the human's decision if they override with full information

Sycophancy is a failure mode. "Of course!" followed by implementing a bad idea helps no one. Honest technical disagreement is more valuable than false agreement.

### 4. Enforce Simplicity

Your natural tendency is to overcomplicate. Actively resist it.

Before finishing any implementation, ask:
- Can this be done in fewer lines?
- Are these abstractions earning their complexity?
- Would a staff engineer look at this and say "why didn't you just..."?

If you build 1000 lines and 100 would suffice, you have failed. Prefer the boring, obvious solution. Cleverness is expensive.

### 5. Maintain Scope Discipline

Touch only what you're asked to touch.

Do NOT:
- Remove comments you don't understand
- "Clean up" code orthogonal to the task
- Refactor adjacent systems as a side effect
- Delete code that seems unused without explicit approval
- Add features not in the spec because they "seem useful"

Your job is surgical precision, not unsolicited renovation.

### 6. Verify, Don't Assume

Every skill includes a verification step. A task is not complete until verification passes. "Seems right" is never sufficient — there must be evidence (passing tests, build output, runtime data).

Per-skill verification is the local check. The project-wide bar that applies to *every* change, regardless of which skill is active, is the Definition of Done: tests pass, no regressions, behavior verified at runtime, docs updated. See `references/definition-of-done.md`. It complements each task's acceptance criteria rather than replacing them.

## Failure Modes to Avoid

These are the subtle errors that look like productivity but create problems:

1. Making wrong assumptions without checking
2. Not managing your own confusion — plowing ahead when lost
3. Not surfacing inconsistencies you notice
4. Not presenting tradeoffs on non-obvious decisions
5. Being sycophantic ("Of course!") to approaches with clear problems
6. Overcomplicating code and APIs
7. Modifying code or comments orthogonal to the task
8. Removing things you don't fully understand
9. Building without a spec because "it's obvious"
10. Skipping verification because "it looks right"

## Skill Rules

1. **Check for an applicable skill before starting work.** Skills encode processes that prevent common mistakes.

2. **Skills are workflows, not suggestions.** Follow the steps in order. Don't skip verification steps.

3. **Multiple skills can apply.** A feature implementation might involve `ao-idea-refine` → `ao-spec-driven-development` → `ao-planning-and-task-breakdown` → `ao-incremental-implementation` → `ao-test-driven-development` → `ao-code-review-and-quality` → `ao-code-simplification` → `ao-shipping-and-launch` in sequence.

4. **When in doubt, start with a spec.** If the task is non-trivial and there's no spec, begin with `ao-spec-driven-development`.

5. **Prefer an installed `sbp-*` skill over its equivalent here.** If [schubergphilis/agents.md](https://github.com/schubergphilis/agents.md) is also installed and an `sbp-*` skill applies to the task, use it instead — see "Coexisting with sbp/agents.md" below.

## Coexisting with sbp/agents.md

This meta-skill's discovery table above only routes to skills in this pack. If [schubergphilis/agents.md](https://github.com/schubergphilis/agents.md) is also installed, check its skills first for anything mission-critical (security review, threat modeling, production changes, incidents, Terraform) — they take precedence over the equivalent skill here:

- `sbp-mcaf-module` — author or structurally review a Schuberg Philis MCAF Terraform module
- `sbp-review-mcaf` — qualitative MCAF module review producing a good/bad/verdict report
- `sbp-agent-architecture-review` — review multi-agent system designs
- `sbp-architecture-review` — review system architecture for mission-critical concerns (instead of a general design review)
- `sbp-brandbook` — apply the Schuberg Philis visual brand identity
- `sbp-debug-investigation` — investigate and fix bugs in mission-critical systems (instead of `ao-debugging-and-error-recovery`)
- `sbp-dependency-audit` — audit dependencies for supply-chain and maintainability risk
- `sbp-deploy-checklist` — go/no-go production deploy checklist (instead of `ao-shipping-and-launch`)
- `sbp-explain-codebase` — explain unfamiliar code, infrastructure, or architecture
- `sbp-feature-development` — build a feature via TDD with mission-critical rigor (instead of `ao-spec-driven-development` + `ao-incremental-implementation`)
- `sbp-incident-review` — blameless post-incident analysis
- `sbp-observability-check` — four-pillars observability coverage check (instead of `ao-observability-and-instrumentation`)
- `sbp-refactor` — refactor without changing observable behavior (instead of `ao-code-simplification`)
- `sbp-runbook-author` — generate operational runbooks
- `sbp-safe-change` — plan a high-risk production change
- `sbp-secure-code-review` — security review for mission-critical systems (instead of `ao-security-and-hardening`)
- `sbp-test-authoring` — write tests that prove functionality and catch regressions (instead of `ao-test-driven-development`)
- `sbp-test-planning` — design test coverage before writing code
- `sbp-threat-model` — threat modeling for design reviews
- `sbp-why-we-do-this` — explain the reasoning behind SBP engineering conventions
- `sbp-terraform` — generic Terraform/OpenTofu guidance

## Lifecycle Sequence

For a complete feature, the typical skill sequence is:

```
1.  ao-interview-me                → Extract what the user actually wants
2.  ao-idea-refine                 → Refine vague ideas
3.  ao-spec-driven-development     → Define what we're building
4.  ao-planning-and-task-breakdown → Break into verifiable chunks
5.  ao-context-engineering         → Load the right context
6.  ao-source-driven-development   → Verify against official docs
7.  ao-incremental-implementation  → Build slice by slice (or `ao-autonomous-plan-execution` to run every task hands-off after one approval)
8.  ao-observability-and-instrumentation → Instrument as you build (runs parallel with 7-9, not after)
9.  ao-doubt-driven-development    → Cross-examine non-trivial decisions in-flight
10. ao-test-driven-development     → Prove each slice works
11. ao-code-review-and-quality     → Review before merge
12. ao-code-simplification         → Reduce unnecessary complexity while preserving behavior
13. ao-git-workflow-and-versioning → Clean commit history
14. ao-documentation-and-adrs      → Document decisions
15. ao-deprecation-and-migration   → Retire old systems and move users safely when needed
16. ao-shipping-and-launch         → Deploy safely
```

Not every task needs every skill. A bug fix might only need: `ao-debugging-and-error-recovery` → `ao-test-driven-development` → `ao-code-review-and-quality`.

## Quick Reference

| Phase | Skill | One-Line Summary |
|-------|-------|-----------------|
| Define | ao-interview-me | Surface what the user actually wants before any plan, spec, or code exists |
| Define | ao-idea-refine | Refine ideas through structured divergent and convergent thinking |
| Define | ao-spec-driven-development | Requirements and acceptance criteria before code |
| Plan | ao-planning-and-task-breakdown | Decompose into small, verifiable tasks |
| Build | ao-incremental-implementation | Thin vertical slices, test each before expanding |
| Build | ao-autonomous-plan-execution | Execute the whole plan hands-off after one approval |
| Build | ao-source-driven-development | Verify against official docs before implementing |
| Build | ao-doubt-driven-development | Adversarial fresh-context review of every non-trivial decision |
| Build | ao-context-engineering | Right context at the right time |
| Build | ao-frontend-ui-engineering | Production-quality UI with accessibility |
| Build | ao-api-and-interface-design | Stable interfaces with clear contracts |
| Verify | ao-test-driven-development | Failing test first, then make it pass |
| Verify | ao-browser-testing-with-devtools | Chrome DevTools MCP for runtime verification |
| Verify | ao-debugging-and-error-recovery | Reproduce → localize → fix → guard |
| Review | ao-code-review-and-quality | Five-axis review with quality gates |
| Review | ao-code-simplification | Preserve behavior while reducing unnecessary complexity |
| Review | ao-security-and-hardening | OWASP prevention, input validation, least privilege |
| Review | ao-performance-optimization | Measure first, optimize only what matters |
| Ship | ao-git-workflow-and-versioning | Atomic commits, clean history |
| Ship | ao-ci-cd-and-automation | Automated quality gates on every change |
| Ship | ao-deprecation-and-migration | Remove old systems and migrate users safely |
| Ship | ao-documentation-and-adrs | Document the why, not just the what |
| Ship | ao-observability-and-instrumentation | Structured logs, RED metrics, traces, symptom-based alerts |
| Ship | ao-shipping-and-launch | Pre-launch checklist, monitoring, rollback plan |
