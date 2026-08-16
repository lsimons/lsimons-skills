"""Thin subprocess helpers with an explicit dry-run flag.

Probing (`command_exists`) is read-only and always runs for real, so
`--dry-run` output reflects the machine's actual state; only the mutating
helpers are skipped.
"""

import shutil
import subprocess
from pathlib import Path

from scripts.console import dry, error


def command_exists(cmd: str) -> bool:
    """Return True if `cmd` is on PATH."""
    return shutil.which(cmd) is not None


def run(
    cmd: list[str],
    *,
    dry_run: bool = False,
    cwd: Path | None = None,
) -> int:
    """Run `cmd` and return its exit status. Returns 0 without running in dry-run."""
    if dry_run:
        dry(f"would run: {' '.join(cmd)}")
        return 0
    return subprocess.run(cmd, check=False, cwd=cwd).returncode


def npm_install_global(package: str, *, dry_run: bool = False) -> bool:
    """Install an npm package globally (into the active mise node).

    `package` must carry an exact `name@version` spec — callers pin, this
    helper does not choose. `--ignore-scripts` is passed unconditionally:
    npm blocks lifecycle scripts by default already, so this only makes
    that guarantee explicit and independent of the host's npm config.
    Neither package this repo installs needs an install script; the one
    thing that does (agent-browser's Chrome build) is fetched by an
    explicit `agent-browser install` instead.
    """
    if dry_run:
        dry(f"would run: npm install -g --ignore-scripts {package}")
        return True
    if not command_exists("npm"):
        error("npm not found; install node (`mise install`) first")
        return False
    return run(["npm", "install", "-g", "--ignore-scripts", package]) == 0
