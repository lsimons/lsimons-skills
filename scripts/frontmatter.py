"""Editing of the YAML frontmatter block at the top of a `SKILL.md`.

Vendoring a skill means changing a few of its declared fields: the `name:`
must match the directory we installed it under, and some skills are given
`disable-model-invocation: true` so only a human typing the name can reach
them (see `skills/mp-writing-for-agents/SKILL-MECHANICS.md`).

Both are structured data, so neither belongs in `skill-rewrites.toml`, which
exists for prose. They are declared in `upstream-skills.toml` and applied
here.

Edits are line-oriented rather than a YAML round-trip: parsing and re-dumping
would reflow quoting, key order and comments across the whole header, turning
every re-fetch into an unreviewable diff of someone else's file. So a field is
one line, and only its line is touched. A field whose value continues onto an
indented line (a block scalar) is refused rather than mangled.
"""

from collections.abc import Iterable, Mapping
from pathlib import Path

DELIMITER = "---"

# One field's declared value. TOML booleans render as YAML booleans.
FieldValue = str | bool


class FrontmatterError(ValueError):
    """A `SKILL.md` frontmatter block is missing, malformed, or unsafe to edit."""


def render(value: FieldValue) -> str:
    """Render a declared value as the YAML text after `key: `."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return value


def split(text: str) -> tuple[list[str], list[str]]:
    """Split `text` into its frontmatter lines and everything from the closing
    delimiter onwards.

    Raises FrontmatterError if the file does not open with a `---` delimiter
    or never closes it.
    """
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].strip() != DELIMITER:
        raise FrontmatterError("file does not start with a '---' frontmatter delimiter")
    for index, line in enumerate(lines[1:], start=1):
        if line.strip() == DELIMITER:
            return lines[1:index], lines[index:]
    raise FrontmatterError("frontmatter block is never closed by '---'")


def _find(block: Iterable[str], key: str) -> int | None:
    """Return the index in `block` of the line declaring `key`, if any."""
    prefix = f"{key}:"
    for index, line in enumerate(block):
        if line.startswith(prefix):
            return index
    return None


def _reject_continuation(block: list[str], index: int, key: str) -> None:
    """Refuse to rewrite a field whose value spills onto indented lines."""
    following = block[index + 1 : index + 2]
    if following and following[0].startswith((" ", "\t")):
        raise FrontmatterError(f"'{key}' is a multi-line value; refusing to rewrite it")


def set_field(text: str, key: str, value: FieldValue, *, require_existing: bool = False) -> str:
    """Return `text` with `key` declared as `value` in its frontmatter.

    An existing declaration is replaced in place; a new one is appended to the
    end of the block, which is valid wherever the preceding field ends. With
    `require_existing`, a missing field is an error instead — that is what
    renaming wants, since a `SKILL.md` without a `name:` is broken, not
    incomplete.
    """
    block, rest = split(text)
    line = f"{key}: {render(value)}\n"

    index = _find(block, key)
    if index is None:
        if require_existing:
            raise FrontmatterError(f"no '{key}:' frontmatter field")
        block = [*block, line]
    else:
        _reject_continuation(block, index, key)
        block[index] = line

    return "".join([DELIMITER + "\n", *block, *rest])


def apply_fields(path: Path, fields: Mapping[str, FieldValue]) -> bool:
    """Apply `fields` to the frontmatter of `path`. Returns True if it changed.

    Raises FrontmatterError, naming the file, on anything it will not edit.
    """
    if not path.is_file():
        raise FrontmatterError(f"{path} does not exist")

    text = path.read_text()
    updated = text
    for key, value in fields.items():
        try:
            updated = set_field(updated, key, value)
        except FrontmatterError as exc:
            raise FrontmatterError(f"{path}: {exc}") from exc

    if updated == text:
        return False
    path.write_text(updated)
    return True


def field_value(text: str, key: str) -> str | None:
    """Return the raw text declared for `key`, or None if it is absent."""
    block, _ = split(text)
    index = _find(block, key)
    if index is None:
        return None
    return block[index].split(":", 1)[1].strip()
