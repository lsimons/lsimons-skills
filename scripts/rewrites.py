"""Deterministic replay of the cross-reference rewrites in `skill-rewrites.toml`.

Renaming a vendored skill breaks every reference to its old name in other
skills' prose. Those references cannot be fixed by find-and-replace: many
upstream skill names are also ordinary words (`research`, `implement`,
`terraform`, `brainstorming`), so a whole-word substitution would mangle
sentences that were never talking about a skill.

The judgement therefore lives in `skill-rewrites.toml`, authored by an agent
(see AGENTS.md) and reviewed as a normal diff. This module only replays it,
so that re-fetching a skill re-applies the same edits without another agent
run. A rule whose `old` text is absent is reported as stale rather than
silently ignored — that is the signal that upstream changed and the agent
needs to look again.

Format, keyed by local skill name then by path relative to the skill
directory:

    ["ao-using-agent-skills"]
    "SKILL.md" = [
      ["--> interview-me", "--> ao-interview-me"],
    ]
"""

import tomllib
from pathlib import Path
from typing import Any, NamedTuple, cast

from scripts.paths import REWRITES_FILE

# skill -> relative path -> [(old, new), ...]
RewriteRules = dict[str, dict[str, list[tuple[str, str]]]]


class Rewrite(NamedTuple):
    """One literal substitution within one file of one skill."""

    skill: str
    relative_path: str
    old: str
    new: str

    def describe(self) -> str:
        """Return a one-line, greppable description of this rule."""
        return f"{self.skill}/{self.relative_path}: {self.old!r} -> {self.new!r}"


class RewriteResult(NamedTuple):
    """What replaying a skill's rules actually did."""

    applied: list[Rewrite]
    stale: list[Rewrite]
    replacements: int


def load_rewrites(path: Path = REWRITES_FILE) -> RewriteRules:
    """Read and validate the rewrite ruleset. A missing file means no rules."""
    if not path.is_file():
        return {}

    rules: RewriteRules = {}
    for skill, files in tomllib.loads(path.read_text()).items():
        where = f"{path}: [{skill!r}]"
        if not isinstance(files, dict):
            raise ValueError(f"{where}: expected a table of '<relative path>' = [[old, new], ...]")
        rules[skill] = {
            relative_path: _parse_pairs(pairs, f"{where} {relative_path!r}")
            for relative_path, pairs in files.items()  # pyright: ignore[reportUnknownVariableType]
        }
    return rules


def _parse_pairs(pairs: Any, where: str) -> list[tuple[str, str]]:
    """Validate one file's list of `[old, new]` pairs."""
    if not isinstance(pairs, list):
        raise ValueError(f"{where}: expected a list of [old, new] pairs")
    parsed: list[tuple[str, str]] = []
    for pair in cast(list[object], pairs):
        if not isinstance(pair, list) or len(cast(list[object], pair)) != 2:
            raise ValueError(f"{where}: expected [old, new] pairs of strings, got: {pair!r}")
        old, new = cast(list[object], pair)
        if not isinstance(old, str) or not isinstance(new, str):
            raise ValueError(f"{where}: expected [old, new] pairs of strings, got: {pair!r}")
        if not old:
            raise ValueError(f"{where}: 'old' text must not be empty")
        parsed.append((old, new))
    return parsed


def apply_rewrites(skill: str, skill_dir: Path, rules: RewriteRules) -> RewriteResult:
    """Apply `skill`'s rules under `skill_dir`, reporting what matched.

    Every rule is applied to every occurrence in its file. A rule whose file
    is missing, or whose `old` text no longer appears, lands in `stale`.
    """
    applied: list[Rewrite] = []
    stale: list[Rewrite] = []
    replacements = 0

    for relative_path, pairs in rules.get(skill, {}).items():
        target = skill_dir / relative_path
        text = target.read_text() if target.is_file() else None
        for old, new in pairs:
            rule = Rewrite(skill, relative_path, old, new)
            if text is None or old not in text:
                stale.append(rule)
                continue
            replacements += text.count(old)
            text = text.replace(old, new)
            applied.append(rule)
        if text is not None:
            target.write_text(text)

    return RewriteResult(applied=applied, stale=stale, replacements=replacements)
