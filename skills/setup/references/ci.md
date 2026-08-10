# How to set up continuous integration of git projects

Unless the project is completely static or completely local, continuous integration should be set up to do automated builds and checks of the project to keep it secure and under quality control.

There should be a configuration that runs for every PR and a configuration that runs for every change to main.

If the project has no CI set up yet:
* If the project is using GitHub, offer the user to set up basic CI using GitHub Actions.
   * Create `.github/workflows/ci.yml` based on template [github-ci-template.yml](../assets/github-ci-template.yml).
   * Upgrade the pinned github actions dependencies to their latest stable versions.
   * If `zizmor` is available, run it to review the template: `zizmor .github/workflows/ci.yml`. Make any needed adjustments.
   * Keep only the steps and caches that match `mise tasks` and the actual project tooling.
* If the project is using GitLab, offer the user to set up basic CI using GitLab CI.
   * Create `.gitlab-ci.yml` based on template [gitlab-ci-template.yml](../assets/gitlab-ci-template.yml), which is an example for Python-based projects.
   * Switch to an appropriate different docker image for projects without Python.
   * Upgrade the docker image used to its latest stable version.
   * Keep only the steps and caches that match `mise tasks` and the actual project tooling.
   * Note this template doesn't pin the mise version, since that's not easily handled in GitLab CI.
* Otherwise, inform the user this skill doesn't have instructions for setting up CI.

For general advice, refer users to the [github actions documentation](https://docs.github.com/en/actions) or the [gitlab ci documentation](https://docs.gitlab.com/topics/build_your_application/).
