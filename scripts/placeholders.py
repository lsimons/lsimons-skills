"""Keep the placeholder token lists inlined in skill prose in sync with the templates.

A skill that writes a file from a template has to verify no placeholder
(`<like this>`) survived into what it wrote. It cannot discover those tokens at
run time: the skill runs in *another* repository, so there is no reliable path
back to its own `assets/` directory. So the token list is inlined in the skill's
prose, and this script generates it at build time from the templates themselves.

A skill marks the generated region with a marker pair:

    <!-- placeholders: assets/README-template.md -->
    ```
    <short description>
    ```
    <!-- /placeholders -->

The target path is relative to the skill's own directory. Ending it in `/`
targets a directory, and the block then lists every template under it that
declares tokens, grouped by file.

`placeholder-tokens.toml` lists tokens that are *meant* to survive into the
written file — `<task>` in the mise templates, `<color>` in the issue-tracker
docs — because they are parts of documented CLI examples, not blanks to fill in.
"""

import argparse
import re
import sys
import tomllib
from pathlib import Path
from typing import NamedTuple

from scripts.console import error, info, success
from scripts.paths import DISABLED_DIR, PLACEHOLDER_IGNORE_FILE, SKILLS_DIR

# A placeholder never spans a line and never nests, which is what rules out the
# markdown and HTML around it.
TOKEN_RE = re.compile(r"<[^<>\n]+>")

BLOCK_RE = re.compile(
    r"(?P<open><!-- placeholders: (?P<target>[^\s>]+) -->\n)"
    r"(?P<body>.*?)"
    r"(?P<close><!-- /placeholders -->)",
    re.DOTALL,
)

# Templates are text; `skills/sbp-brandbook/assets` is SVG and PNG.
TEMPLATE_SUFFIXES = (".md", ".txt", ".toml", ".yml", ".yaml")


class Drift(NamedTuple):
    """One generated block whose inlined list no longer matches its templates."""

    path: Path
    target: str
    expected: str
    actual: str


def load_ignores(path: Path | None = None) -> dict[str, tuple[str, ...]]:
    """Load the per-template lists of tokens that belong in the written file.

    Keys are template paths relative to `skills/` or `disabled/`, so a skill
    moving between the two does not invalidate them.
    """
    path = path or PLACEHOLDER_IGNORE_FILE
    data = tomllib.loads(path.read_text())
    ignore: object = data.get("ignore", {})
    if not isinstance(ignore, dict):
        raise ValueError(f"{path}: [ignore] must be a table")
    return {str(key): tuple(str(token) for token in value) for key, value in ignore.items()}  # pyright: ignore[reportUnknownVariableType, reportUnknownArgumentType]  # tomllib returns Any-typed values


def _template_key(template: Path) -> str:
    """The `placeholder-tokens.toml` key for a template: `<skill>/<path in skill>`."""
    root = SKILLS_DIR if SKILLS_DIR in template.parents else DISABLED_DIR
    return template.relative_to(root).as_posix()


def extract_tokens(template: Path, ignores: dict[str, tuple[str, ...]]) -> list[str]:
    """Return the placeholder tokens a template declares, sorted and deduplicated."""
    ignored = set(ignores.get(_template_key(template), ()))
    found = set(TOKEN_RE.findall(template.read_text()))
    return sorted(found - ignored, key=str.casefold)


def stale_ignores(ignores: dict[str, tuple[str, ...]]) -> list[str]:
    """Return `<key>: <token>` for every ignore entry that matches nothing on disk."""
    stale: list[str] = []
    for key, tokens in sorted(ignores.items()):
        candidates = [SKILLS_DIR / key, DISABLED_DIR / key]
        template = next((path for path in candidates if path.is_file()), None)
        if template is None:
            stale.append(f"{key}: no such template")
            continue
        present = set(TOKEN_RE.findall(template.read_text()))
        stale.extend(f"{key}: {token}" for token in tokens if token not in present)
    return stale


def _skill_root(path: Path) -> Path:
    """The skill directory containing `path` (the child of `skills/` or `disabled/`)."""
    for parent in path.parents:
        if parent.parent in (SKILLS_DIR, DISABLED_DIR):
            return parent
    raise ValueError(f"{path} is not inside a skill directory")


def _resolve_targets(skill_root: Path, target: str) -> list[Path]:
    """The templates a block's target names: one file, or every template in a directory."""
    resolved = skill_root / target
    if target.endswith("/"):
        return sorted(p for p in resolved.iterdir() if p.suffix in TEMPLATE_SUFFIXES)
    if not resolved.is_file():
        raise ValueError(f"{skill_root.name}: no such template: {target}")
    return [resolved]


def render_body(skill_root: Path, target: str, ignores: dict[str, tuple[str, ...]]) -> str:
    """Render the fenced token list for one block, including its trailing newline."""
    lines: list[str] = ["```"]
    for template in _resolve_targets(skill_root, target):
        tokens = extract_tokens(template, ignores)
        if not tokens:
            continue
        if target.endswith("/"):
            lines.append(f"{target}{template.name}")
            lines.extend(f"  {token}" for token in tokens)
        else:
            lines.extend(tokens)
    lines.append("```")
    return "\n".join(lines) + "\n"


def _sync_file(path: Path, ignores: dict[str, tuple[str, ...]], apply: bool) -> list[Drift]:
    """Regenerate one file's blocks, writing it back if `apply` and anything drifted."""
    skill_root = _skill_root(path)
    text = path.read_text()
    drifted: list[Drift] = []
    rewritten: list[str] = []
    end = 0
    for match in BLOCK_RE.finditer(text):
        expected = render_body(skill_root, match["target"], ignores)
        if match["body"] != expected:
            drifted.append(Drift(path, match["target"], expected, match["body"]))
        rewritten.append(text[end : match.start()])
        rewritten.append(f"{match['open']}{expected}{match['close']}")
        end = match.end()
    if drifted and apply:
        rewritten.append(text[end:])
        _ = path.write_text("".join(rewritten))
    return drifted


def sync_blocks(apply: bool) -> list[Drift]:
    """Check — or with `apply`, rewrite — every generated block under `skills/`.

    Returns the blocks that did not match. With `apply` they have been rewritten,
    so the return value is the list of what changed.
    """
    ignores = load_ignores()
    drifted: list[Drift] = []
    for path in sorted(SKILLS_DIR.rglob("*.md")):
        if "<!-- placeholders:" in path.read_text():
            drifted.extend(_sync_file(path, ignores, apply))
    return drifted


def main(argv: list[str] | None = None) -> int:
    """Check the inlined placeholder lists, or rewrite them with `--apply`."""
    parser = argparse.ArgumentParser(
        description="Keep skill prose's placeholder token lists in sync with the templates."
    )
    _ = parser.add_argument(
        "--apply",
        action="store_true",
        help="rewrite drifted blocks instead of failing",
    )
    args = parser.parse_args(argv)

    stale = stale_ignores(load_ignores())
    for entry in stale:
        error(f"stale ignore in {PLACEHOLDER_IGNORE_FILE.name}: {entry}")

    drifted = sync_blocks(apply=args.apply)
    for drift in drifted:
        relative = drift.path.relative_to(SKILLS_DIR.parent)
        if args.apply:
            info(f"rewrote {relative} [{drift.target}]")
        else:
            error(f"out of date: {relative} [{drift.target}]")
            error(f"  expected:\n{drift.expected}")
            error(f"  found:\n{drift.actual}")

    if stale:
        return 1
    if drifted and not args.apply:
        error("run `mise run placeholders-fix` to update them")
        return 1
    success("placeholder lists are up to date" if not drifted else "placeholder lists updated")
    return 0


if __name__ == "__main__":
    sys.exit(main())
