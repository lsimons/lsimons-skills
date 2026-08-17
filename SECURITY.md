# Security Policy

## Personal project

This is a personal project.

Do not depend on this project.

In particular, do not depend on this project for its security.

There is no good mechanism configured for security updates.

There is no support available.

## Scope

Almost everything under `skills/` and `disabled/` is **vendored** third-party
content, fetched from the upstreams listed in `upstream-skills.toml`. A problem
in a vendored skill belongs upstream — report it there, and this repository will
pick the fix up on the next `mise run skills-update`. What *is* in scope here is
the Python tooling under `scripts/`, the CI workflows, and the choice of which
upstreams to vendor at all.

## Reporting a vulnerability

Please use the "Report a vulnerability" button under the
[Security tab](https://github.com/lsimons/lsimons-skills/security) of the GitHub
project. Private vulnerability reporting is enabled.

If you cannot use GitHub's vulnerability reporting workflow, contact
[@lsimons](https://github.com/lsimons) by any route listed on that profile.
