"""Find surviving references to the upstream names of renamed skills.

This is the report an agent triages after a fetch: every whole-word
occurrence of an upstream skill name that this repository vendors under a
different name. The scan deliberately over-reports — `research` and
`terraform` are both skill names and ordinary words — because deciding which
occurrences actually mean the skill is the judgement that `skill-rewrites.toml`
records. See AGENTS.md.
"""

import re
import sys
from pathlib import Path
from typing import NamedTuple

from scripts.manifest import SkillEntry, load_manifest
from scripts.paths import SKILLS_DIR

# Skill text lives in markdown; scripts and assets are not prose to triage.
SCANNED_SUFFIXES = (".md",)


class Reference(NamedTuple):
    """One line mentioning a renamed skill's upstream name.

    `local_names` holds every skill that upstream name could now mean. It has
    more than one entry when two packs ship the same name (osmani and
    superpowers both ship `test-driven-development`), in which case which one
    a given line means is a judgement call, not a lookup.
    """

    path: Path
    lineno: int
    upstream_name: str
    local_names: tuple[str, ...]
    line: str

    @property
    def ambiguous(self) -> bool:
        """True if more than one vendored skill claims this upstream name."""
        return len(self.local_names) > 1


def _word_pattern(name: str) -> re.Pattern[str]:
    """Match `name` as a whole token, so `ao-tdd` does not match `tdd`."""
    return re.compile(rf"(?<![\w-]){re.escape(name)}(?![\w-])")


def scan_references(
    entries: list[SkillEntry],
    skills_dir: Path = SKILLS_DIR,
) -> list[Reference]:
    """Return every mention of a renamed skill's upstream name, in path order.

    A skill's own directory is scanned too: upstream frequently refers to
    its own skills by name, and those references need renaming as well.
    """
    renamed: dict[str, list[str]] = {}
    for entry in entries:
        if entry.renamed:
            renamed.setdefault(entry.upstream_name, []).append(entry.local_name)
    patterns = {name: _word_pattern(name) for name in renamed}

    found: list[Reference] = []
    for path in sorted(skills_dir.rglob("*")):
        if not path.is_file() or path.suffix not in SCANNED_SUFFIXES:
            continue
        for lineno, line in enumerate(path.read_text(errors="replace").splitlines(), start=1):
            for upstream_name, pattern in patterns.items():
                if pattern.search(line):
                    candidates = tuple(renamed[upstream_name])
                    found.append(Reference(path, lineno, upstream_name, candidates, line.strip()))
    return found


def group_by_skill(references: list[Reference]) -> dict[str, list[Reference]]:
    """Group references by the upstream name they mention, most-referenced first."""
    grouped: dict[str, list[Reference]] = {}
    for reference in references:
        grouped.setdefault(reference.upstream_name, []).append(reference)
    return dict(sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])))


def main(argv: list[str] | None = None) -> int:
    """Print every candidate reference as `path:line: text`, one per line.

    This is the triage worklist (`mise run skills-refs`). It re-scans what is
    on disk, so it reflects the rewrites already replayed by the last fetch.
    """
    _ = argv
    for reference in scan_references(load_manifest().entries):
        relative = reference.path.relative_to(SKILLS_DIR.parent)
        targets = " | ".join(reference.local_names)
        print(
            f"{relative}:{reference.lineno}: "
            f"[{reference.upstream_name} -> {targets}] {reference.line}"
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
