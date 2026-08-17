# How to set up mise in a new project

Check if `.mise.toml` or `mise.toml` exists in the root of the project.

If neither file exists, then further initialize mise.

Create `.mise.toml` from an appropriate template:

* [Mise template for Python](../assets/mise-template-py.toml)
* [Mise template for TypeScript](../assets/mise-template-ts.toml)
* [Mise template for Go](../assets/mise-template-go.toml)
* [Mise template for Rust](../assets/mise-template-rs.toml)
* [Mise template for Starlight](../assets/mise-template-doc.toml)

If you cannot determine the type of project, use the Python template.

If you started from a template:

* Remove any `mise` tools that are not used in the project.
* Remove any `mise` commands that don't exist / don't work.

Add any `mise` commands that should typically exist based on the tools that are available.

Run `mise trust` if needed.

Make sure mise has dependency cooldowns enabled: `mise settings set -l minimum_release_age=7d`.

Make sure mise lockfiles are enabled: `mise settings set -l lockfile=true`.

If there is a `mise.lock`, update with `mise lock`. Otherwise, generate a lockfile with `mise lock --platform linux-x64,macos-arm64,windows-x64`.

Run `mise doctor` to see if anything needs fixing.

If you changed `.mise.toml` or `mise.toml`, run `mise fmt` to format the file.
