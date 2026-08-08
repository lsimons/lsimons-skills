"""Prefixed status messages, so script output is greppable by severity."""

import sys


def info(msg: str) -> None:
    """Print an info message."""
    print(f"[INFO] {msg}")


def success(msg: str) -> None:
    """Print a success message."""
    print(f"[SUCCESS] {msg}")


def warn(msg: str) -> None:
    """Print a warning message."""
    print(f"[WARN] {msg}")


def error(msg: str) -> None:
    """Print an error message to stderr."""
    print(f"[ERROR] {msg}", file=sys.stderr)


def dry(msg: str) -> None:
    """Print a dry-run message."""
    print(f"[DRY-RUN] {msg}")
