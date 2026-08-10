# How to set up continuous integration of git projects

Unless the project is completely static or completely local, continuous integration should be set up to do automated builds and checks of the project to keep it secure and under quality control.

CI should run both for every PR / merge request and for every change to main. Both templates below do that in a single configuration file with two triggers.

If the project has no CI set up yet:
* If the project is using GitHub, offer the user basic CI using GitHub Actions. Recommend yes; it is one file, and it is what the rest of this skill assumes.
   * Create `.github/workflows/ci.yml` based on template [github-ci-template.yml](../assets/github-ci-template.yml).
   * Upgrade the pinned github actions dependencies to their latest stable versions.
   * Keep only the steps and caches that match `mise tasks` and the actual project tooling.
   * If `zizmor` is available, run it over the result and make any needed adjustments:
     ```bash
     GH_TOKEN=$(gh auth token 2>/dev/null) zizmor --collect=all --strict-collection .
     ```
     This covers the workflows and `.github/dependabot.yml` in one pass. See [dependencies.md](./dependencies.md) for what the token buys.
   * Optionally, also run `actionlint`. It answers *will this workflow run and do what I meant*, where zizmor answers *is this workflow safe* — neither substitutes for the other. Rank it below zizmor: it earns its place once the workflows contain non-trivial `run:` blocks and expressions, which the scaffolded template does not.

     It is in mise's registry as `aqua:rhysd/actionlint`, and picks up shellcheck automatically when shellcheck is present. What it checks that zizmor does not: workflow schema, `${{ }}` expression type-checking against the contexts actually available for each trigger, runner labels, the `needs:` graph, and shellcheck over every `run:` block. What zizmor checks that it does not: permissions, pinning, injection, and everything else in the security catalogue.
* If the project is using GitLab, offer the user basic CI using GitLab CI. Recommend yes.
   * Create `.gitlab-ci.yml` based on template [gitlab-ci-template.yml](../assets/gitlab-ci-template.yml), which is an example for Python-based projects.
   * Switch to an appropriate different docker image for projects without Python.
   * Upgrade the docker image used to its latest stable version.
   * Keep only the steps and caches that match `mise tasks` and the actual project tooling.
   * Note this template doesn't pin the mise version, since that's not easily handled in GitLab CI.
   * Validate it with `glab ci lint`. That is server-side: it checks `.gitlab-ci.yml` against the real project, resolving `include:` and project context, which no local linter can do. Offline, the fallback is the official CI JSON schema via `check-jsonschema --schemafile https://gitlab.com/gitlab-org/gitlab/-/raw/master/app/assets/javascripts/editor/schema/ci.json .gitlab-ci.yml`.
* Otherwise, inform the user this skill doesn't have instructions for setting up CI.

## GitLab: validation exists, security auditing does not

There is no zizmor equivalent for GitLab CI, and no linter will supply one. The reason is structural rather than a missing tool: most GitLab CI hardening is not expressible in the YAML. There is no `pull_request_target` analogue, fork pipelines are opt-in and run in the fork's context, and `CI_JOB_TOKEN` scoping, protected variables and protected branches are **project settings**.

So for GitLab the equivalent of "audit the workflow" is "audit the project settings". Point the human at the `CI_JOB_TOKEN` allowlist, protected variables, protected branches, and fork-pipeline permissions, and say plainly that the linter covers none of it.

For general advice, refer users to the [github actions documentation](https://docs.github.com/en/actions) or the [gitlab ci documentation](https://docs.gitlab.com/topics/build_your_application/).
