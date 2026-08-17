---
name: research
description: investigate a topic to enable decision-making, searching the web for details, reading documentation, following references, producing a markdown report
argument-hint: [issue or details]
model: opus
---

Your task is to gather all relevant detail from primary sources, analyze it, and produce a report as a new markdown file in this repo. Do not create new source code or new tests.

If a number or issue id is provided as an argument, look up the ticket details in the issue tracker. If the issue is unassigned, assign it to yourself.

First, ensure the research question is clear. Ask the user questions to clarify if needed.

If you can use a subagent, use it to do the actual research. If you can background the subagent, do so, so other work can continue in parallel.

Use web searches and web fetches, if those are available, to ground the research in current facts available online.

Investigate the research question against primary sources: official docs, source code, specs, first-party APIs. Do not rely on secondary write-ups. Follow claims back to their source and verify them.

Write the research findings to a single markdown file citing all sources.

Save the file according to the repo conventions if available. Otherwise, put it in a sensible location and share it.

Use `/complete` to finish up if that skill is available.
