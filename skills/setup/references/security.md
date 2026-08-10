# How to set up security instructions in git projects

If this file does not exist it means the project may receive security incident reports in various ways.

It would be good if the project authors can decide a preferred route for handling security.

But you cannot decide this for them and we don't need to bother the user with it immediately.

For small personal open source projects, you can use this template and process it:

* [SECURITY-template.md](../assets/SECURITY-template.md)
   * Replace <User> with the user's identity:
      * for GitHub projects, prefer `@handle`, find with `gh auth status --json hosts --jq '.hosts["github.com"][0]["login"]'`
      * for GitLab projects, prefer `@handle`, find with `glab auth status 2>&1 | grep "Logged in"`
      * otherwise, prefer <Firstname> <Lastname>, find with `git config --get user.name`
   * Replace <User> with the user's identity as done for the code of conduct.
   * When the repo host is not gitHub, remove the specific GitHub instructions in favor of e-mail based vulnerability reporting.

## Deciding on and implementing a security policy

_Actually_ deciding a security policy is real work, most of it for humans.

Setting up a basic SECURITY.md file helps the humans to get started, but much more effort is needed to create secure software, and the policy is just a small part of that. The policy should be aligned with how secure the project and its processes are.

The [guide from GitHub](https://docs.github.com/en/code-security) is a reasonable start. Refer users to it if they ask for advice.
