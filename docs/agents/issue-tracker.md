# Issue tracker: GitHub

Issues for this project are managed as GitHub issues.

The issues live in the same remote as the source code (the GitHub default):
[lsimons/lsimons-skills](https://github.com/lsimons/lsimons-skills/issues).

Use the `gh` CLI for all operations.

You can learn about the `gh` issue CLI with `gh issue --help`.

## Labels

The following issue labels are used:

```
NAME               DESCRIPTION                                        COLOR
bug                Something isn't working                            #d73a4a
documentation      Improvements or additions to documentation         #0075ca
duplicate          This issue or pull request already exists          #cfd3d7
enhancement        New feature or request                             #a2eeef
good first issue   Good for newcomers                                 #7057ff
help wanted        Extra attention is needed                          #008672
invalid            This doesn't seem right                            #e4e669
question           Further information is requested                   #d876e3
needs-triage       Maintainer needs to evaluate this issue            #e6e6fa
needs-info         Waiting on reporter for more information           #e6e6fa
ready-for-agent    Fully specified, ready for an autonomous agent     #e6e6fa
ready-for-human    Requires human implementation                      #e6e6fa
wontfix            This will not be worked on                         #ffffff
```

Three more labels are applied by dependabot, not by hand:
`dependencies`, `github_actions`, `python:uv`.

## Triage flow

The five lavender-and-white labels above are the workflow ones. An issue starts
at `needs-triage`, then moves to exactly one of:

* `needs-info` — cannot proceed until the reporter answers something.
* `ready-for-agent` — specified well enough that an autonomous agent can pick it
  up and finish it without further judgement calls.
* `ready-for-human` — needs a decision, a licensing call, or an upstream
  conversation that is not an agent's to make.
* `wontfix` — closed without action.

## Where a report belongs

Almost everything under `skills/` and `disabled/` is vendored from the upstreams
in `upstream-skills.toml`. A bug in a vendored skill belongs in *that* upstream's
tracker; fixing it here does not stick, because the next
`mise run skills-update` overwrites it. Issues that do belong here:

* the Python tooling in `scripts/`, the mise tasks, or CI;
* which upstreams are vendored, under what prefix, and whether a skill is
  enabled;
* a cross-reference that needs a rule in `skill-rewrites.toml`.

See [`../../AGENTS.md`](../../AGENTS.md) for the full working agreements.
