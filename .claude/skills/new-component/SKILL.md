---
name: new-component
description: Scaffold a new dashboard UI component with its component-library story and tests, following the library's props, accessibility and state conventions.
disable-model-invocation: true
argument-hint: <component_name> [one-line purpose]
---

Create the component `$ARGUMENTS` in `frontend/dashboard/components/`.

## Before writing

Read `frontend/dashboard/components/README.md` — it is the source of truth for
the props conventions, the accessibility rules and the loading/empty/error
matrix. Read one existing component of the same kind and its story
(`primitives.py` + `library/story_chip.py` is a good pair) and follow them.
If the name or purpose is unclear, ask before writing.

## Files to touch

1. **Component** — add it to the module that fits (`primitives.py`,
   `feedback.py`, `controls.py`, `card.py`), or a new module only if none does.
   - Primary data positional, everything else keyword-only (`*,`).
   - `key: str` required if it owns widgets; `help` and `disabled` where they apply.
   - Pure state → `on_click` / `on_change` callbacks. I/O → return the intent.
   - Colour never alone: text and/or icon too. Escape user text. Truncate long
     text keeping the full value in `title=` / `help=`.
   - Pure HTML builders go in `markup.py` so they can be unit tested.
   - CSS: reuse tokens from `tokens.py`; new rules go in `styles.py` under a
     `.tm-<name>` class.
2. **Export** — add it to `components/__init__.py` (import + `__all__`, sorted).
3. **Story** — `library/story_<name>.py` with `render()`, built on `_shell.py`
   (`story_header`, `canvas`, `controls_row`, `code_block`). Show every state
   from the README matrix: default, long text, empty, error, disabled, wrapping.
4. **Navigation** — register the story in `frontend/component_library.py`
   under the right section.
5. **Tests** — add the story to `_STORIES` in `frontend/tests/test_library.py`;
   unit-test any pure helper in `frontend/tests/test_components.py`.
6. **Docs** — add a row to the components table in the root `README.md` and,
   if it has edge cases, a row to the matrix in `components/README.md`.

## Done when

`/ci-local` passes and the story renders in the library (`.\run.ps1 library`
→ http://localhost:8502) in both the light and dark themes.
