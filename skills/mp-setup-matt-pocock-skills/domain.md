# Domain Docs

How the engineering skills should consume this repo's domain documentation when exploring the codebase.

## Before exploring, read these

- **`CONTEXT.md`** at the repo root, or
- **`CONTEXT-MAP.md`** at the repo root if it exists — it points at one `CONTEXT.md` per context. Read each one relevant to the topic.
- **The repo's decision-record corpus** — `docs/adr/` if it exists, otherwise `docs/spec/` (see [ADR-FORMAT.md](../mp-domain-modeling/ADR-FORMAT.md) for which one a repo uses and why). Read entries that touch the area you're about to work in. In multi-context repos, also check `src/<context>/docs/adr/` (or `docs/spec/`) for context-scoped decisions.

If any of these files don't exist, **proceed silently**. Don't flag their absence; don't suggest creating them upfront. The `/mp-domain-modeling` skill (reached via `/mp-grill-with-docs` and `/mp-improve-codebase-architecture`) creates them lazily when terms or decisions actually get resolved — defaulting to `docs/spec/` when the repo has neither yet.

## File structure

Single-context repo (most repos):

```
/
├── CONTEXT.md
├── docs/spec/
│   ├── S01-event-sourced-orders.md
│   └── S02-postgres-for-write-model.md
└── src/
```

(Or `docs/adr/` with `0001-slug.md` numbering, if that's what the repo already had before these skills were introduced.)

Multi-context repo (presence of `CONTEXT-MAP.md` at the root):

```
/
├── CONTEXT-MAP.md
├── docs/spec/                         ← system-wide decisions
└── src/
    ├── ordering/
    │   ├── CONTEXT.md
    │   └── docs/spec/                 ← context-specific decisions
    └── billing/
        ├── CONTEXT.md
        └── docs/spec/
```

## Use the glossary's vocabulary

When your output names a domain concept (in an issue title, a refactor proposal, a hypothesis, a test name), use the term as defined in `CONTEXT.md`. Don't drift to synonyms the glossary explicitly avoids.

If the concept you need isn't in the glossary yet, that's a signal — either you're inventing language the project doesn't use (reconsider) or there's a real gap (note it for `/mp-domain-modeling`).

## Flag decision-record conflicts

If your output contradicts an existing decision record, surface it explicitly rather than silently overriding:

> _Contradicts ADR-0007 (event-sourced orders) — but worth reopening because…_
> _Contradicts S01 (event-sourced orders) — but worth reopening because…_
