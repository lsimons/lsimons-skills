# How to set up a prose project

A **prose project** is a repository whose product is the markdown itself: research notes,
source critiques, decision records, specifications, a handbook, a memo and its evidence
base. There may be a script or two, but there is no application and often no site.

Signals, from exploration:

* `.md` files heavily outnumber source files, and the source files that exist are
  generators or fetchers rather than an application.
* Documents cross-reference each other by heading anchor.
* Directories named `docs/notes/`, `docs/adr/`, `docs/spec/`, `sources/`, `raw/`.
* No test framework, no build output that anyone consumes.

Do **not** confuse this with a documentation *site* (Starlight, Docusaurus, MkDocs), which
has a build, a dev server and dependencies — that is
[mise-template-doc.toml](../assets/mise-template-doc.toml). A prose project has three
quality gates and no build.

Skip the *Unit tests* section of the skill entirely for these. There is nothing to test,
and a scaffolded hello-world test is noise.

## The three gates

Start from [mise-template-prose.toml](../assets/mise-template-prose.toml):
`markdownlint-cli2` for style, `lychee` for links, `typos` for spelling, and a `ci` task
that depends on all three.

Each wants a config file, and in each case the config is where project-specific reality
gets recorded — resist working around a check inline.

### `.markdownlint-cli2.yaml`

```yaml
config:
  # Prose wraps at 90 by hand, but quoted headlines and generated tables run
  # long. A hard limit would mean rewrapping quotations, which loses fidelity.
  MD013: false
  # Duplicate headings are legitimate when every file in a directory uses the
  # same section names.
  MD024:
    siblings_only: true
  # Inline HTML is used for <a id> anchors and <details> blocks.
  MD033: false

globs:
  - "**/*.md"

ignores:
  # Verbatim text we do not own and must not reformat.
  - "CODE_OF_CONDUCT.md"
  # Machine extractions of .pptx/.docx/.pdf. Regenerable, and reformatting them
  # would break the "this is what the source says" guarantee.
  - "**/*.pptx.md"
```

**Verbatim third-party text gets a nested `.markdownlint-cli2.yaml` in its own
directory**, never a relaxation of the root config. A captured standards document will
violate a dozen rules for reasons that are the source's, not the project's; scoping the
exemption to that directory keeps the root config honest about the hand-written prose.

### `lychee.toml`

```toml
max_retries = 3
timeout = 30
max_concurrency = 8

exclude = [
  # Not real URLs — placeholders and examples in prose.
  "^https?://example\\.(com|org)",
  # A private repository answers 404 to unauthenticated requests, so its own
  # URL fails the check from a CI runner.
]

# Many publishers and vendors bot-block HEAD requests from CI.
accept = ["200", "206", "403", "429"]

# Do not follow into verbatim archives or third-party PDFs.
exclude_path = ["sources", "dist"]
```

**Run it with `--include-fragments`.** This is the point of the whole gate. External URLs
rot slowly; internal anchors break the moment someone renames a heading, and in a
repository where documents cite each other's sections that is a broken citation. Checking
fragments makes the cross-reference graph verifiable, which in turn makes it safe to
require descriptive anchor links instead of bare identifiers.

### `_typos.toml`

```toml
[files]
extend-exclude = [
  # Verbatim archives: their "typos" are the source's, or are minified JS.
  "sources/**/*.html",
]

[default.extend-words]
# Names the dictionary does not know. Add them here rather than rephrasing.
```

## Scheduled CI

Add a weekly `schedule:` trigger to the CI workflow alongside `push` and `pull_request`.
External links rot with no commit to blame, so a repository that is quiet for a month
should still find out that a cited source moved.

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:
  schedule:
    - cron: "17 6 * * 1"
```

## Ask about pull requests

A prose repository with one regular author is the case where the PR ritual costs more than
it buys: a review request nobody is waiting to answer, delaying a change that is a
formality. `mise run ci` plus the CI run on `main` is the safety net the PR would have
provided.

Ask the user, recommending "commit straight to `main`" for a single-author repository and
"keep pull requests" for anything with real reviewers. Whatever they choose, **write it
down in both `CONTRIBUTING.md` and `AGENTS.md`** — for agents it contradicts the usual
default, so it has to be stated as an override rather than an omission.

## Where the writing rules live

A prose project accumulates house rules — how sources get graded, how claims cite their
provenance, where speculation goes. Put them in `CONTRIBUTING.md` once, and have
`AGENTS.md` link to that section rather than restating it. Two copies of the same seven
rules drift, and the agent file is the copy that stops being read.
