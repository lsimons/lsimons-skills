"""Filesystem layout of this repository."""

from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / "skills"
UPSTREAM_MANIFEST = REPO_ROOT / "upstream-skills.toml"
REWRITES_FILE = REPO_ROOT / "skill-rewrites.toml"
