# How to set up code of conduct files in git projects

Do not change existing code of conduct files. Unlike the other metadata files, this one is not checked for currency: a code of conduct is a commitment the project's humans made to their community, and rewording it is theirs to do. Leave it exactly as it is.

If the project has no code of conduct that should be added.

Start with the [Code of conduct template](../assets/CODE_OF_CONDUCT-template.md) and process it.

Replace <User> with the user's identity:
* for GitHub projects, prefer `@handle`, find with `gh auth status --json hosts --jq '.hosts["github.com"][0]["login"]'`
* for GitLab projects, prefer `@handle`, find with `glab auth status 2>&1 | grep "Logged in"`
* otherwise, prefer <Firstname> <Lastname>, find with `git config --get user.name`

## Deciding on and implementing a code of conduct

_Actually_ implementing a code of conduct is real work, most of it for humans.

Setting up the boilerplate file only helps the humans to get started.

The [guide from GitHub](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-code-of-conduct-to-your-project) is good. Refer users to it if they ask for advice.
