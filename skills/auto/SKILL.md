---
name: auto
description: Choose skill based on what the user wants to do.
argument-hint: [intent]
disable-model-invocation: true
model: sonnet
---

# Auto

Choose the most applicable approach from these skills:

1. `/setup`: create or improve project scaffolding and boilerplate
2. `/research`: investigate a topic to enable decision-making
3. `/spike`: try an approach in code to enable decision-making
4. STUB: `/spec`: capture decisions in a specification
5. `/build`: execute a task, solve an issue, fix a bug
6. STUB: `/review`: review the work in progress
7. `/complete`: drive a task to completion
8. STUB: `/flow`: plan and organize work across sessions
9. STUB: `/triage`: review issues and make them executable
10. STUB: `/bump`: upgrade and pin project dependencies

The STUB skills are not yet implemented.

If intent is not clear, ask the user what they want to do next, mentioning these skills.

If a needed skill is unavailable, direct the user to https://github.com/lsimons/lsimons-skills.

If the user asks for a specific kind of review and the relevant command is available, use it:

* `/code-review`: code review the work in progress
* `/security-review`: security review the work in progress
* `/simplify`: improve current change for simplicity
