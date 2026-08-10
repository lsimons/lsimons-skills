# Issue tracker: Local Markdown

Issues for this project are managed in markdown files committed into the repo.

The issues live in the same repo as the source code.

Group multiple related issues into plans. For example, a new epic, large feature, or module may get one plan file that contains of many issues.

The plans should have a name of `docs/plan/PNN-<slug>.md`.

## Plan and issue template

The plans can be based on this template:

```
# PNN — <title>

<short plan description>

<references to relevant specs>

## Issues

### PNN.N <issue title> - <issue status> <YYYY-MM-DD>

Labels: <label-A>, <label-B>
Related:
- PNN.N <issue title>
- PNN.N <issue title>

<issue description>
```

The datetime for an issue is updated whenever work is done on the issue. Initially it will be the creation date of the issue. For completed issues it will be the date the issue was completed.

Labels and related issues are optional fields.

## Labels

Use these labels:

| Label           | Description                                    |
| --------------- | ---------------------------------------------- |
| bug             | Something isn't working                        |
| documentation   | Improvements or additions to documentation     |
| enhancement     | New feature or request                         |
| needs-triage    | Maintainer needs to evaluate this issue        |
| needs-info      | Waiting on reporter for more information       |
| ready-for-agent | Fully specified, ready for an autonomous agent |
| ready-for-human | Requires human implementation                  |
| wontfix         | This will not be worked on                     |
