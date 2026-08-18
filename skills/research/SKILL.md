---
name: research
description: investigate a topic to enable decision-making, searching the web for details, reading documentation, following references, producing a markdown report
argument-hint: [issue or details]
model: opus
---

Your task is to gather all relevant detail from primary sources, analyze it, and produce a report as a new markdown file in this repo. Do not create new source code or new tests.

If a number or issue id is provided as an argument, look up the ticket details in the issue tracker. If the issue is unassigned, assign it to yourself.

First, ensure the research question is clear. Ask the user questions to clarify if needed.

Choose a short title for the research, and from that a slug that is lowercase and kebab case.

Run `date +%F` to get the current date.

Unless the project does not use branches, if you are on the main branch, start a new branch. Follow the project naming convention for branches if it exists, otherwise use `research/<YYYY-MM-DD>-<slug>`.

Unless the project does not use worktrees, if you are not in a worktree, do the work in a new worktree.

## Investigation

Break the research question down into independent sub-questions. If you can use subagents, fan out one subagent per sub-question and synthesize their results into the single report.

Use web searches and web fetches, if those are available, to ground the research in current facts available online.

Investigate the research question against primary sources: official docs, source code, specs, first-party APIs. Do not rely on secondary write-ups. Follow claims back to their source and verify them.

## Report

Write the research findings to a single markdown file citing all sources.

If the project has a convention for where to put research, use it. Otherwise, save the report as `docs/research/<YYYY-MM-DD>-<slug>.md` and share the path, so that later spikes and specs can link to it.

## Verification

* Check that the research question stated at the top of the report is actually answered by the report.
* Check that every substantive claim carries a citation.
* Check that the cited sources are primary — official docs, source code, specs, first-party APIs — and not secondary write-ups.
* Check that no source code and no tests were created.

Do not loop or iterate on fixes. If there are significant gaps — a sub-question left unanswered, a claim resting only on a secondary source — record them as open questions in the report rather than papering over them.

Report the findings: a summary of what was learned and what remains open, with a link to the detailed report.

## Session completion

Use `/complete` to finish up if that skill is available.

If there is an issue associated with the research, add a comment pointing to the report, and include the summary of findings in the comment.
