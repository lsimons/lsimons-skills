---
name: spike
description: try an approach in code to enable decision-making, creating throwaway code, prototyping, testing an approach, answering a question by trying to implement a quick answer
argument-hint: [issue or details]
model: sonnet
---

Your task is to create a prototype or some throwaway code to test a particular approach or hypothesis or to answer a particular question, exploring a design, answering a question quickly so that a decision on the full implementation can be made.

If a number or issue id is provided as an argument, look up the ticket details in the issue tracker. If the issue is unassigned, assign it to yourself.

Choose a short title for the spike, and from that a slug that is lowercase and kebab case.

Run `date +%F` to get the current date.

Unless the project does not use branches, if you are on the main branch, start a new branch. Follow the project naming convention for branches if it exists, otherwise use `spikes/<YYYY-MM-DD>-<slug>`.

Unless the project does not use worktrees, if you are not in a worktree, do the work in a new worktree.

If the project has a convention for where to put spike code, use it. Otherwise, put the spike content in a sensible location and share it, such as a directory `spikes/<YYYY-MM-DD>-<slug>/`.

## Exploration

Read the repo and form a plan before changing anything. Look at relevant local research, specs, code, tests, and other spikes, but do not do extensive research.

Add a `README.md` inside the spike directory based on [README-template.md](./assets/README-template.md) with your plan. All plans need title, short description, hypothesis, and validation plan. Judge what other sections you need and delete the rest.

The plan should focus on the simplest and fastest way possible to test the hypothesis. Normal project quality standards do not apply; do not apply project quality gates. You can skip unit tests, formatting, linting, CI, detailed specs, and so on.

Present a plan summary to the user with a link to the detailed README.md file.

## Implementation

Implement the spike by executing the plan. Keep any code, data, specs, tests and other new files inside the spike directory.

Update the spike README.md with a description of and pointers to the implementation.

##  Instruction

If the spike contains runnable code or tests, run them, and also include instructions on how to run them again in the README.md.

## Validation

After implementation is done, execute your validation plan and update the spike README with validation results.

Analyze and synthesize the implementation and the results into key findings and lessons learned and update the README with those.

## Verification

* Check the README.md is complete: assert every placeholder token listed below
  is absent from the spike README.md. A bare `grep '<'` is the wrong check.
* Check that implementation files are referenced from the README.md.
* Check that the lessons learned actually follow from the implementation.
* Check that the hypothesis is confirmed or rejected.

The placeholder tokens [README-template.md](./assets/README-template.md) declares:

<!-- placeholders: assets/README-template.md -->
```
<Description of how to run implementation commands and tests>
<Description of what is built to test the hypothesis>
<How to confirm or reject the hypothesis>
<Key takeaways>
<Links to key existing documentation>
<Problem we are trying to solve by testing this hypothesis>
<short description>
<Testable statement to explore>
<title>
<What happened applying the validation plan to the implementation>
<YYYY-MM-DD>
```
<!-- /placeholders -->

That list is generated from the template. If it is empty, this skill is broken:
stop and report it rather than treating no tokens as no placeholders.

Do not loop or iterate on fixes. If there are significant gaps, add appropriate caveats to the Lessons learned in the spike README.md.

Report the spike results: a summary of the implementation done and the lessons learned, with a link to the detailed README.md.

## Session completion

Unless specified otherwise, spike branches do not need to be merged or pushed to main and do not need a pull request. Do offer to commit and push the branch. If it is available, use the `/complete` skill for this, but be clear not to make a PR, not to merge, not to run quality gates.

If there is an issue associated with the spike, add a comment to point to the spike branch, and include the Lessons learned in the comment.
