"""Claude Code PostToolUse hook: lint-fix and format every edited Python file.

Runs the same ruff (and the same pyproject.toml config) as CI, so code written in
a Claude Code session is already clean before it reaches a commit. Issues ruff
cannot fix on its own are sent back to Claude (exit code 2) so it fixes them.

Needs ruff on the host, pinned like requirements-dev.txt:
    python -m pip install ruff==0.16.6
Without it the hook is a no-op, so the repo still works for anyone who clones it.
"""

import importlib.util
import json
import subprocess
import sys


def main() -> int:
    path = json.load(sys.stdin).get("tool_input", {}).get("file_path", "")
    if not path.endswith(".py"):
        return 0
    if importlib.util.find_spec("ruff") is None:
        print(
            "ruff not installed; skipping (pip install ruff==0.16.6)", file=sys.stderr
        )
        return 0

    ruff = [sys.executable, "-m", "ruff"]
    # Fix first, then format, so the formatter tidies what the fixes leave.
    # --force-exclude keeps pyproject's excludes in force for explicit paths.
    check = subprocess.run(
        [*ruff, "check", "--fix", "--quiet", "--force-exclude", path],
        capture_output=True,
        text=True,
        check=False,
    )
    subprocess.run([*ruff, "format", "--quiet", "--force-exclude", path], check=False)
    if check.returncode != 0:
        print(check.stdout + check.stderr, file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
