"""Parsing of `upstream-skills.txt`, the manifest of fetched skills."""

from pathlib import Path
from typing import NamedTuple

from scripts.paths import UPSTREAM_MANIFEST


class SkillEntry(NamedTuple):
    """One `<repository-url> <skill-name>` line of the manifest."""

    repository: str
    name: str


def load_manifest(path: Path = UPSTREAM_MANIFEST) -> list[SkillEntry]:
    """Return every skill declared in the manifest, in file order.

    Blank lines and `#` comments are ignored. Any other line must hold
    exactly two whitespace-separated fields.
    """
    entries: list[SkillEntry] = []
    for lineno, raw in enumerate(path.read_text().splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) != 2:
            raise ValueError(
                f"{path}:{lineno}: expected '<repository-url> <skill-name>', got: {line}"
            )
        entries.append(SkillEntry(parts[0], parts[1]))
    return entries
