---
name: ci-local
description: Run the same checks as CI (ruff lint + format check, mypy, pytest with the coverage gate) inside Docker before pushing.
disable-model-invocation: true
---

Run the CI checks locally, in the project's Docker image, and report the result.

1. Lint: `powershell -File ./run.ps1 lint` on Windows, `make lint` elsewhere.
2. Tests: `powershell -File ./run.ps1 test` on Windows, `make test` elsewhere.
   Run it even if lint failed, so both results are known.
3. Report a short summary:
   - ✅ / ❌ per step (ruff check, ruff format, mypy, pytest, coverage ≥ 90 %).
   - Each failure as `path:line — message`.
   - For coverage, the files and missing lines from the `term-missing` report.

Do not fix anything unless asked. If Docker is not running, say so and stop.
