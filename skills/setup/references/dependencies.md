# How to set up basic dependency checks in git projects

To deal with software supply chain security, it's important not to simply download the latest versions of software from the internet, while it's also important to not download software that has active vulnerabilities that affect the project. Secure the project setup following software supply chain best practices:

If the project has third-party dependencies, check it is using strict dependency pinning for those dependencies using the project its chosen dependency managers (`mise`, `uv`, `pnpm`, `cargo`, etc). If it isn't pinning dependencies, change it to add strict dependency pinning.

If the project is set up so git ignores dependency lock files (`pnpm-lock.yaml`, `uv.lock`, etc), change that setup so that the dependency lock files are committed to git and check in the lock files.

If the project is using `mise`, change its tool config to pin to specific tool dependencies. After starting from a template this is usually needed, since the templates may specify "latest".

If the project is using GitHub Actions, change all GitHub actions to pin to a specific version and SHA.

If the project is using GitHub then it should use renovate or dependabot or a similar dependency checker. If none are set up, set up dependabot. Create `.github/dependabot.yml` based on [dependabot-template.yml](../assets/dependabot-template.yml). Make sure to remove the packaging ecosystems not actually in use in this project.

If the project is using Github Actions, it should have a GitHub Actions security audit set up. If none is configured, set it up using zizmor.

## Implementing dependency management

_Actually_ implementing dependency management is a lot more work.

For example, it's important to minimize the number and size of dependencies and to periodically audit their quality. The [sbp-dependency-audit](https://github.com/schubergphilis/agents.md/tree/main/skills/sbp-dependency-audit) skill can help with this if it is installed.

Various other work is not as easily handled by AI agents. The github [supply chain security guide](https://docs.github.com/en/code-security/concepts/supply-chain-security/supply-chain-security) is a reasonable start that also has advice on [dependency best practices](https://docs.github.com/en/code-security/concepts/supply-chain-security/best-practices-for-maintaining-dependencies). Refer users to it if they ask for advice.
