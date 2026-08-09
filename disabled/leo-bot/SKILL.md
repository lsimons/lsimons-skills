---
name: leo-bot
description: Ask which skill fits your situation. One router over every mp-, ao-, s- and sbp- skill installed here.
disable-model-invocation: true
---

# Leo Bot

You don't remember every skill, so ask. This is the single router over four
packs that all cover the same ground in different styles:

| Pack | Source | Character |
| --- | --- | --- |
| `sbp-*` | Schuberg Philis | Mission-critical bar: blast radius, rollback, the 3 AM test |
| `mp-*` | Matt Pocock | One long flow, interview-heavy, stateful docs and tickets |
| `ao-*` | Addy Osmani | Phase-per-skill checklists across the whole lifecycle |
| `s-*` | superpowers | Small set of terse process primitives |

Route in three steps, in order.

## Step 0 — is OpenSpec in this repo?

Check before anything else:

```bash
ls openspec/ 2>/dev/null && echo "openspec present"
```

If an `openspec/` directory exists at the repo root, this project has its own
project-local OpenSpec skills and `/opsx:*` slash commands. **Prefer those for
anything spec-, plan- or change-shaped** — proposing a change, writing the
spec, breaking it into tasks, applying it, archiving it. They are wired to this
repo's actual `openspec/` state, and the generic spec skills here are not.

Don't guess the command names — list what the project actually installed
(`.claude/commands/opsx/`, `.claude/skills/`) or run `openspec --help`.

OpenSpec covers the spec/change lifecycle only. Everything outside it —
debugging, review, security, Terraform, testing mechanics, git — still routes
through the steps below.

## Step 1 — is this mission-critical?

Mission-critical means: it runs in production, other people depend on it, and
being wrong costs more than being slow. Customer-facing systems, anything with
auth or secrets in it, infrastructure, anything you'd be paged for.

**If yes, use the `sbp-*` skill.** It runs a stricter bar than the general
engineering packs, and that bar is the point. Take it over the equivalent
below without waiting to be asked.

| Situation | Skill |
| --- | --- |
| Build a feature that will reach production | `sbp-feature-development` |
| Design coverage before writing code | `sbp-test-planning` |
| Write the tests themselves | `sbp-test-authoring` |
| Chase a bug where "works on my machine" won't do | `sbp-debug-investigation` |
| Change the shape of code before a feature | `sbp-refactor` |
| Review code for security | `sbp-secure-code-review` |
| Review a system's architecture (SPOFs, blast radius, rollback) | `sbp-architecture-review` |
| Review a multi-agent system design | `sbp-agent-architecture-review` |
| Threat-model a design | `sbp-threat-model` |
| Audit dependencies for supply-chain and bloat risk | `sbp-dependency-audit` |
| Check monitoring, alerting, logging coverage | `sbp-observability-check` |
| Plan a high-risk production change | `sbp-safe-change` |
| Decide go/no-go on a deploy | `sbp-deploy-checklist` |
| Write an operational runbook | `sbp-runbook-author` |
| Post-incident analysis | `sbp-incident-review` |
| Understand unfamiliar code or infrastructure | `sbp-explain-codebase` |
| Explain why an SBP convention exists | `sbp-why-we-do-this` |
| Any Terraform / OpenTofu module | `sbp-terraform` |
| An MCAF module specifically | `sbp-mcaf-module` (authoring/structure), `sbp-review-mcaf` (qualitative review) |
| Anything that represents SBP visually | `sbp-brandbook` |

There is no `sbp-*` skill for the *upstream* half of the work — sharpening a
raw idea, interviewing, writing a spec, breaking work into tickets, git
mechanics, frontend craft, performance. For those, drop to step 2 and use the
pack you picked there.

## Step 2 — pick one dev pack, and stay in it

For everything that isn't mission-critical and isn't OpenSpec's, choose **one**
of `mp-*`, `ao-*`, `s-*`.

All three are good. **Combining them is not.** They overlap almost completely
and disagree on the details — three test-first skills, three review skills,
three planning skills, each assuming its own artifacts and vocabulary. Running
`s-brainstorming` into `ao-planning-and-task-breakdown` into `mp-implement`
means each step is looking for state the previous one never wrote. Pick a lane
and finish the task in it.

If the user hasn't expressed a preference, ask once and then commit for the
rest of the session:

- **`mp-*`** — you want the strongest thinking-before-building, a repo that
  accumulates `CONTEXT.md`, ADRs and tickets, and work spread across many
  sessions. Highest ceremony, highest payoff on genuinely fuzzy work.
- **`ao-*`** — you want a named checklist for each phase of the lifecycle,
  including the ones the others skip (frontend, API design, performance,
  observability, CI/CD, deprecation).
- **`s-*`** — you want the minimum: a short process primitive per situation and
  nothing to maintain. Best for a bounded task in a repo you already know.

Once the choice is made, say which pack you're in, then route within it.

### mp — the main flow

`/mp-grill-with-docs` (or `/mp-grill-me` outside a working directory)
→ `/mp-to-spec` → `/mp-to-tickets` → `/mp-implement` per ticket, `/clear`ing
between them. `/mp-implement` drives `/mp-tdd` internally and closes with
`/mp-code-review`. Skip straight to `/mp-implement` when it's a single-session
build.

Keep the grilling, spec, and tickets in one unbroken context window.

| Situation | Skill |
| --- | --- |
| Sharpen an idea, leaving a paper trail | `mp-grill-with-docs` |
| Sharpen an idea with no repo under it | `mp-grill-me` |
| The interview primitive itself | `mp-grilling` |
| Turn the conversation into a spec | `mp-to-spec` |
| Split a spec into tracer-bullet tickets | `mp-to-tickets` |
| Build a ticket or spec | `mp-implement` |
| Build one behaviour test-first | `mp-tdd` |
| Review a branch or PR against a fixed point | `mp-code-review` |
| A hard, intermittent, or crept-in bug | `mp-diagnosing-bugs` |
| Incoming bugs and requests to sort | `mp-triage` |
| An effort too big for one session to hold | `mp-wayfinder` |
| Answer a design question with throwaway code | `mp-prototype` |
| Delegate reading to a background agent | `mp-research` |
| Design a module's shape (depth, seams) | `mp-codebase-design` |
| Survey the codebase for deepening opportunities | `mp-improve-codebase-architecture` |
| Pin down domain terminology, record an ADR | `mp-domain-modeling` |
| Carry work to a new harness, directory, or colleague | `mp-handoff` |
| Resolve an in-progress merge/rebase conflict | `mp-resolving-merge-conflicts` |
| Steps only a human can do (credentials, dashboards) | `mp-wizard` |
| Ask someone else the questions you can't answer | `mp-to-questionnaire` |
| That last message didn't land | `mp-wait-what` |
| Learn a concept over several sessions | `mp-teach` |
| Write a skill, AGENTS.md, or agent-facing doc | `mp-writing-for-agents` |
| First-time setup of the tracker and doc layout | `mp-setup-matt-pocock-skills` |

`/mp-ask-leo` is this pack's own router, with the flow diagram in full and the
phase-boundary decision tree. Read it when the routing question is *within* the
pack.

### ao — one skill per phase

| Situation | Skill |
| --- | --- |
| Don't know what you want yet | `ao-interview-me` |
| Rough concept, want variants | `ao-idea-refine` |
| New project, feature, or change, no spec | `ao-spec-driven-development` |
| Have a spec, need tasks | `ao-planning-and-task-breakdown` |
| Implementing code | `ao-incremental-implementation` |
| Run the whole plan hands-off after one approval | `ao-autonomous-plan-execution` |
| Set up context for a session or project | `ao-context-engineering` |
| Need doc-verified, source-cited code | `ao-source-driven-development` |
| High stakes or unfamiliar code | `ao-doubt-driven-development` |
| UI work | `ao-frontend-ui-engineering` |
| API or module boundary design | `ao-api-and-interface-design` |
| Writing or running tests | `ao-test-driven-development` |
| Verifying in a real browser | `ao-browser-testing-with-devtools` |
| Something broke | `ao-debugging-and-error-recovery` |
| Reviewing code | `ao-code-review-and-quality` |
| Code works but is too complex | `ao-code-simplification` |
| Untrusted input, auth, secrets | `ao-security-and-hardening` |
| Slow, or a suspected regression | `ao-performance-optimization` |
| Committing, branching, releasing | `ao-git-workflow-and-versioning` |
| Build or deploy pipeline | `ao-ci-cd-and-automation` |
| Removing an old system, migrating users | `ao-deprecation-and-migration` |
| Recording a decision or writing docs | `ao-documentation-and-adrs` |
| Logs, metrics, traces, alerts | `ao-observability-and-instrumentation` |
| Deploying or launching | `ao-shipping-and-launch` |

`/ao-using-agent-skills` is this pack's own router; it also carries the core
operating behaviors (surface assumptions, manage confusion, push back, enforce
simplicity, scope discipline, verify) worth reading once.

### s — process primitives

| Situation | Skill |
| --- | --- |
| Any creative or build work, before code | `s-brainstorming` |
| Have a spec, need a written plan | `s-writing-plans` |
| Executing a plan in a separate session, with checkpoints | `s-executing-plans` |
| Executing independent tasks in this session | `s-subagent-driven-development` |
| 2+ independent tasks, no shared state | `s-dispatching-parallel-agents` |
| Need an isolated workspace first | `s-using-git-worktrees` |
| Implementing any feature or bugfix | `s-test-driven-development` |
| Any bug, test failure, unexpected behavior | `s-systematic-debugging` |
| About to claim it's done, fixed, or passing | `s-verification-before-completion` |
| Want your finished work reviewed | `s-requesting-code-review` |
| Received review feedback | `s-receiving-code-review` |
| Done and tests pass — how to integrate | `s-finishing-a-development-branch` |
| Creating or editing a skill | `s-writing-skills` |

`/s-using-superpowers` is this pack's own router.

## Crossing lanes

Two exceptions to "stay in one pack":

- **Step 1 always wins.** If the task turns mission-critical mid-flow — the
  change is going to production, the code touches auth — switch to the `sbp-*`
  skill for that step and return to your lane afterwards. Don't average the two
  bars; pick the one the system actually needs.
- **Skills with no equivalent elsewhere** are fair game from any lane, because
  there's nothing to conflict with: `mp-wizard`, `mp-resolving-merge-conflicts`,
  `mp-writing-for-agents`, `s-writing-skills`, `s-using-git-worktrees`,
  `ao-frontend-ui-engineering`, `ao-browser-testing-with-devtools`,
  `ao-performance-optimization`, `ao-ci-cd-and-automation`.

Everything outside these four packs — `1password`, `claude-history`,
`memex-*`, `python-knowledge-patch`, `vercel-*`, `an-frontend-design` — is a
tool or reference, not a process, and composes with any lane.

## Finishing a task

Once code changes exist and the remaining work is mechanical — quality
gates, commit, push, watch CI — use `complete` regardless of lane. It picks
`gh`, `glab`, or plain `git` based on the remote URL and drives to a pushed,
green-CI state without a check-in per step. It's not a plan runner; for
running a whole multi-task plan hands-off after one approval, that's still
`ao-autonomous-plan-execution`.
