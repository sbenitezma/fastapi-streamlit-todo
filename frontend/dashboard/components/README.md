# `dashboard/components` — UI component library

Reusable, accessible render functions for the dashboard. **Not** web components —
Streamlit functions composed from `st.*`. Live examples: `streamlit run frontend/gallery.py`.

## Architecture

```
components/
  tokens.py      design tokens (colour / space / radius) — mirrored in styles.py :root
  markup.py      pure HTML builders: truncate, badge_html   (unit tested)
  primitives.py  badge · chip · chip_row · meter
  feedback.py    load · empty_state · error_state          (the three non-happy paths)
  controls.py    segmented_filter · pager · confirm_button
  card.py        card
```

- **Presentational only.** Components take data + callbacks, render, and return the
  user's *intent*. No HTTP, no `app.data`, no business rules.
- **One source of truth per pattern.** Change a badge everywhere by editing `markup.py`
  + the `.tm-badge` rules in `styles.py`.

## Props conventions

| Rule | Why |
|---|---|
| Primary data is **positional**; everything else is **keyword-only** (`*,`) | readable call sites; safe to add options later |
| `key: str` is **required** when the component owns interactive widgets | Streamlit widget identity |
| Pure-state changes → `on_click` / `on_change` **callbacks** (`+ args`) | callbacks run *before* the rerun, so they may mutate widget state |
| Actions with I/O → **return the intent** (`bool` / value), caller keeps `try/except` | exceptions inside a callback surface as an ugly Streamlit error |
| `help: str` passes through to the widget tooltip / `aria-describedby` | discoverability + a11y |
| `disabled: bool` where applicable | consistent affordance |

## Accessibility

- Colour never carries meaning alone — every state also has **text and/or an icon**
  (`badge` word + icon, `card` accent + `tm-title--done`, pager labels are "Previous"/"Next").
- Token colour pairs meet **WCAG AA (≥ 4.5:1)** on any surface, light or dark
  (self-contained bg + white fg).
- `empty_state` is a `role="status"` region; decorative icons are `aria-hidden`.
- Focus ring is global (`styles.py`, 2.4.7); targets are ≥ 40 px (2.5.5);
  `prefers-reduced-motion` disables animation (2.3.3).
- Long text truncates with the full value kept in `title=` / `help=`.

## Loading states & edge cases

| Component | Loading | Empty | Error | Other edge cases |
|---|---|---|---|---|
| `load(loader, key=…)` | `st.spinner` (only on a real fetch, not a cache hit) | — | message + **Retry** + `st.stop()` | caller picks `error_types` |
| `empty_state` | — | *is* the empty state | — | optional CTA; `body` optional |
| `meter` | — | `total<=0` → "No … yet" line | — | `value` clamped to `[0, total]` |
| `badge` | — | empty label → `—` | — | unknown tone → `neutral`; text escaped |
| `chip_row` | — | `[]` → renders nothing | — | wraps when many; static pill if no `on_remove` |
| `pager` | — | first page & no next → renders nothing | — | correct `disabled` on both ends |
| `confirm_button` | — | — | caller wraps the side effect | returns `True` only on the confirm click |

## Responsive

`layout="centered"` (~730 px). Components rely on wrapping primitives:
`st.container(horizontal=True, wrap=True)` (chips) and `st.columns` (auto-stacks
< 640 px). `styles.py` adds a `@media (max-width: 640px)` block (tighter gutters,
smaller badge cap). The sidebar collapses to a drawer on narrow screens.

## Usage

```python
from dashboard.components import (
    badge,
    card,
    meter,
    chip_row,
    pager,
    confirm_button,
    load,
    empty_state,
)

meter(stats["done"], stats["total"], label="done", note=f"{stats['pending']} pending")

with card(accent="warning", muted=False, key=str(tid)):  # key: unique per card
    st.markdown(
        f'<div class="tm-title">{title}{badge_html("◷ Pending", tone="warning")}</div>',
        unsafe_allow_html=True,
    )

data = load(
    lambda: fetch(...), key="todos", spinner="Loading tasks…", error_types=(APIError,)
)
if not data:
    empty_state("No tasks yet", body="Add one from the sidebar.", icon="✅")

if confirm_button("Delete", key=f"del-{tid}", title=title):
    do_delete(tid)

pager(
    key="pager", page=page, has_next=len(page_rows) == PAGE_SIZE, on_change=go_to_page
)
```
