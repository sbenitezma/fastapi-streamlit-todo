"""Claude Code PostToolUse hook: lint-fix and format every edited Python file.

Runs the same ruff (and the same pyproject.toml config) as CI, so code written in
a Claude Code session is already clean before it reaches a commit. Issues ruff
cannot fix on its own are sent back to Claude (exit code 2) so it fixes them.

The ruff version is read from requirements-dev.txt, the pin Dependabot bumps.
On first use of each version it is pip-installed into .claude/.tools/ (ignored
by git, a few seconds) and older copies are removed, so the host never drifts
from CI and nothing is installed into the global Python.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOLS = ROOT / ".claude" / ".tools"


def pinned_version() -> str | None:
    reqs = (ROOT / "requirements-dev.txt").read_text(encoding="utf-8")
    match = re.search(r"^ruff==([\w.]+)", reqs, re.MULTILINE)
    return match.group(1) if match else None


def ruff_binary(version: str) -> Path | None:
    """Path to the pinned ruff, installing it on first use."""
    target = TOOLS / f"ruff-{version}"
    exe = target / "bin" / ("ruff.exe" if os.name == "nt" else "ruff")
    if exe.exists():
        return exe

    print(f"Installing ruff {version} into {TOOLS} ...", file=sys.stderr)
    TOOLS.mkdir(parents=True, exist_ok=True)
    # Install into a temp dir, then rename: parallel edits never see half an install.
    tmp = Path(tempfile.mkdtemp(dir=TOOLS, prefix=".tmp-"))
    pip = subprocess.run(
        [sys.executable, "-m", "pip", "install", "--quiet",
         "--disable-pip-version-check", "--target", str(tmp), f"ruff=={version}"],
        capture_output=True, text=True, check=False,
    )  # fmt: skip
    if pip.returncode != 0:
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"Could not install ruff {version}:\n{pip.stderr}", file=sys.stderr)
        return None
    try:
        tmp.rename(target)
    except OSError:  # another edit installed it first
        shutil.rmtree(tmp, ignore_errors=True)

    for old in TOOLS.glob("ruff-*"):
        if old != target:
            shutil.rmtree(old, ignore_errors=True)
    return exe if exe.exists() else None


def main() -> int:
    path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
    if not path.endswith(".py"):
        return 0
    version = pinned_version()
    exe = ruff_binary(version) if version else None
    if exe is None:
        return 0  # never block an edit because the tooling is unavailable

    # Fix first, then format, so the formatter tidies what the fixes leave.
    # --force-exclude keeps pyproject's excludes in force for explicit paths.
    check = subprocess.run(
        [exe, "check", "--fix", "--quiet", "--force-exclude", path],
        capture_output=True,
        text=True,
        check=False,
    )
    subprocess.run([exe, "format", "--quiet", "--force-exclude", path], check=False)
    if check.returncode != 0:
        print(check.stdout + check.stderr, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
