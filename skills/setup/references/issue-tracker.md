# How to set up basic issue tracking in git projects

## Choosing the issue tracker

If the issue tracker to use is not specified, choose:

* If the project is using a GitHub remote, use the GitHub issue tracker.
* If the project is using a GitLab remote, use the GitLab issue tracker.
* If the project isn't using GitHub or GitLab, use checked-in markdown files for issue tracking.
   * If no location is specified for plans and issues, use `docs/plan/`.

Some other issue trackers in common use are JIRA or Linear.

## Documenting issue labels

For github/gitlab use `gh label list` or `glab label list` to determine the issue labels available.

All these labels should exist:

| Label           | Description                                    | Color   |
| --------------- | ---------------------------------------------- | ------- |
| bug             | Something isn't working                        | #d73a4a |
| documentation   | Improvements or additions to documentation     | #0075ca |
| enhancement     | New feature or request                         | #a2eeef |
| needs-triage    | Maintainer needs to evaluate this issue        | #e6e6fa |
| needs-info      | Waiting on reporter for more information       | #e6e6fa |
| ready-for-agent | Fully specified, ready for an autonomous agent | #e6e6fa |
| ready-for-human | Requires human implementation                  | #e6e6fa |
| wontfix         | This will not be worked on                     | #ffffff |

If some do not exist, list the missing ones and lead with the recommendation — "these five are missing; create them? (recommended: yes)" — so the user can accept in a word. If the user approves, create the additional labels:
* Command for gh: `gh label create <label> -c "NNNNNN" -d "<desc>"`
* Command for glab: `glab label create --name <label> -c "#NNNNNN" -d "<desc>"`

## Documenting issue tracking policy

Record the issue tracker in use in `docs/agents/issue-tracker.md`.

Write this file starting from a basic template:

* GitHub: [issue-tracker-github.md](../assets/issue-tracker-github.md)
* GitLab: [issue-tracker-gitlab.md](../assets/issue-tracker-gitlab.md)
* Local markdown: [issue-tracker-markdown.md](../assets/issue-tracker-markdown.md)
* Other: write it from scratch

Update `docs/agents/issue-tracker.md` with the available labels. (For local markdown, we simply use the above list.)
