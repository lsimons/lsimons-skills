"""Parsing of `upstream-skills.toml`, the manifest of vendored skills.

The manifest declares, per upstream repository, which skills to fetch and
what to call them here. Local names are derived by prefixing, so that skills
from different packs cannot collide (both `lsimons/superpowers` and
`lsimons/osmani-agent-skills` ship a `test-driven-development`).

Renaming a skill is only mechanically half the job: the fetcher renames the
directory and the `name:` frontmatter field, but cross-references inside
skill bodies are prose, and are handled by `scripts.rewrites`. See AGENTS.md.

A source may also declare `frontmatter` overrides, applied by
`scripts.frontmatter` to a fetched skill's YAML header — how a skill is
exposed here is a vendoring decision of the same kind as what it is called
here, so it is declared in the manifest rather than patched after the fact.
"""

import tomllib
from pathlib import Path
from typing import Any, NamedTuple, cast

from scripts.frontmatter import FieldValue
from scripts.paths import UPSTREAM_MANIFEST

# The fetcher owns `name:`, deriving it from the skill's local name.
FRONTMATTER_RESERVED = frozenset({"name"})


class SkillEntry(NamedTuple):
    """One skill to fetch, and the name it takes in this repository."""

    repository: str
    upstream_name: str
    local_name: str
    frontmatter: tuple[tuple[str, FieldValue], ...] = ()
    enabled: bool = False

    @property
    def renamed(self) -> bool:
        """True if this skill is vendored under a different name than upstream."""
        return self.upstream_name != self.local_name

    @property
    def frontmatter_fields(self) -> dict[str, FieldValue]:
        """The declared frontmatter overrides, as a mapping."""
        return dict(self.frontmatter)


class LocalSkill(NamedTuple):
    """One hand-maintained skill, and whether it is active."""

    name: str
    enabled: bool = False


class Source(NamedTuple):
    """One upstream repository and the skills taken from it."""

    repository: str
    prefix: str
    license: str
    copyright: str
    entries: list[SkillEntry]


class Manifest(NamedTuple):
    """The whole manifest: fetched sources plus hand-maintained skills."""

    sources: list[Source]
    local_skills: list[LocalSkill]

    @property
    def entries(self) -> list[SkillEntry]:
        """Every fetched skill, in manifest order."""
        return [entry for source in self.sources for entry in source.entries]

    @property
    def declared_names(self) -> set[str]:
        """Every skill directory this manifest accounts for, fetched or not."""
        return {entry.local_name for entry in self.entries} | {
            local.name for local in self.local_skills
        }

    @property
    def enabled_names(self) -> set[str]:
        """Every skill directory that should live under `skills/`, not `disabled/`."""
        return {entry.local_name for entry in self.entries if entry.enabled} | {
            local.name for local in self.local_skills if local.enabled
        }


def local_name_for(upstream_name: str, prefix: str) -> str:
    """Apply `prefix` to `upstream_name`, unless it already carries it.

    Upstreams that already namespace some of their skills (`sbp-*`,
    `memex-search`) keep the names they have, so one prefix can be declared
    for a whole repository without double-prefixing part of it.
    """
    if not prefix or upstream_name.startswith(prefix):
        return upstream_name
    return f"{prefix}{upstream_name}"


def _require(table: dict[str, object], key: str, kind: type, where: str) -> Any:
    """Return `table[key]`, raising a located error if it is missing or mistyped."""
    if key not in table:
        raise ValueError(f"{where}: missing required key '{key}'")
    value = table[key]
    if not isinstance(value, kind):
        raise ValueError(f"{where}: '{key}' must be a {kind.__name__}, got {type(value).__name__}")
    return value


def _parse_frontmatter(fields: object, where: str) -> tuple[tuple[str, FieldValue], ...]:
    """Validate one skill's frontmatter overrides, preserving declaration order."""
    if fields is None:
        return ()
    if not isinstance(fields, dict):
        raise ValueError(f"{where}: must be a table of '<field>' = <string or boolean>")

    parsed: list[tuple[str, FieldValue]] = []
    for key, value in cast(dict[str, object], fields).items():
        if key in FRONTMATTER_RESERVED:
            raise ValueError(f"{where}: '{key}' is set by the fetcher and cannot be overridden")
        if not isinstance(value, str | bool):
            raise ValueError(f"{where}: '{key}' must be a string or boolean, got {value!r}")
        parsed.append((key, value))
    return tuple(parsed)


def _parse_source(table: dict[str, object], index: int) -> Source:
    """Build one `Source` from a `[[source]]` table."""
    where = f"[[source]] #{index + 1}"
    repository: str = _require(table, "repository", str, where)
    where = f"[[source]] {repository}"

    prefix = table.get("prefix", "")
    if not isinstance(prefix, str):
        raise ValueError(f"{where}: 'prefix' must be a string")

    raw_renames = table.get("rename", {})
    if not isinstance(raw_renames, dict):
        raise ValueError(f"{where}: 'rename' must be a table")
    renames = cast(dict[str, object], raw_renames)

    raw_frontmatter = table.get("frontmatter", {})
    if not isinstance(raw_frontmatter, dict):
        raise ValueError(f"{where}: 'frontmatter' must be a table")
    frontmatter = cast(dict[str, object], raw_frontmatter)

    raw_enabled = table.get("enabled", {})
    if not isinstance(raw_enabled, dict):
        raise ValueError(f"{where}: 'enabled' must be a table")
    enabled = cast(dict[str, object], raw_enabled)
    for skill, value in enabled.items():
        if not isinstance(value, bool):
            raise ValueError(f"{where}: enabled['{skill}'] must be a boolean, got {value!r}")

    skills = cast(list[object], _require(table, "skills", list, where))
    entries: list[SkillEntry] = []
    names: list[str] = []
    for skill in skills:
        if not isinstance(skill, str):
            raise ValueError(f"{where}: 'skills' must contain only strings")
        override = renames.get(skill)
        if override is not None and not isinstance(override, str):
            raise ValueError(f"{where}: rename of '{skill}' must be a string")
        names.append(skill)
        entries.append(
            SkillEntry(
                repository,
                skill,
                override or local_name_for(skill, prefix),
                _parse_frontmatter(frontmatter.get(skill), f"{where}: frontmatter of '{skill}'"),
                bool(enabled.get(skill, False)),
            )
        )

    unknown = sorted(set(renames) - set(names))
    if unknown:
        raise ValueError(f"{where}: renames for skills not listed: {unknown}")

    unknown = sorted(set(frontmatter) - set(names))
    if unknown:
        raise ValueError(f"{where}: frontmatter for skills not listed: {unknown}")

    unknown = sorted(set(enabled) - set(names))
    if unknown:
        raise ValueError(f"{where}: enabled for skills not listed: {unknown}")

    return Source(
        repository=repository,
        prefix=prefix,
        license=_require(table, "license", str, where),
        copyright=_require(table, "copyright", str, where),
        entries=entries,
    )


def load_manifest(path: Path = UPSTREAM_MANIFEST) -> Manifest:
    """Read and validate the manifest.

    Raises ValueError, naming the offending source, on a malformed entry or
    on two declarations claiming the same directory under `skills/`.
    """
    data = tomllib.loads(path.read_text())

    raw_local = data.get("local", [])
    if not isinstance(raw_local, list):
        raise ValueError(f"{path}: 'local' must be a list of strings")
    local_names: list[str] = []
    for name in cast(list[object], raw_local):
        if not isinstance(name, str):
            raise ValueError(f"{path}: 'local' must be a list of strings")
        local_names.append(name)

    raw_local_enabled = data.get("local-enabled", {})
    if not isinstance(raw_local_enabled, dict):
        raise ValueError(f"{path}: 'local-enabled' must be a table")
    local_enabled = cast(dict[str, object], raw_local_enabled)
    for name, value in local_enabled.items():
        if not isinstance(value, bool):
            raise ValueError(f"{path}: local-enabled['{name}'] must be a boolean, got {value!r}")
    unknown = sorted(set(local_enabled) - set(local_names))
    if unknown:
        raise ValueError(f"{path}: 'local-enabled' for skills not listed in 'local': {unknown}")

    local_skills = [LocalSkill(name, bool(local_enabled.get(name, False))) for name in local_names]

    raw_sources = data.get("source", [])
    if not isinstance(raw_sources, list):
        raise ValueError(f"{path}: 'source' must be an array of tables")

    sources: list[Source] = []
    for index, table in enumerate(cast(list[object], raw_sources)):
        if not isinstance(table, dict):
            raise ValueError(f"{path}: [[source]] #{index + 1} must be a table")
        sources.append(_parse_source(cast(dict[str, object], table), index))

    manifest = Manifest(sources=sources, local_skills=local_skills)
    _reject_duplicates(manifest, path)
    return manifest


def _reject_duplicates(manifest: Manifest, path: Path) -> None:
    """Fail if two declarations claim the same directory under `skills/`."""
    seen: dict[str, str] = dict.fromkeys((local.name for local in manifest.local_skills), "local")
    for entry in manifest.entries:
        previous = seen.get(entry.local_name)
        if previous is not None:
            raise ValueError(
                f"{path}: '{entry.local_name}' is declared twice "
                f"(by {previous} and by {entry.repository})"
            )
        seen[entry.local_name] = entry.repository
