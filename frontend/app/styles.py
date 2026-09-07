"""Global CSS: design tokens, component styles, spacing + a11y hardening.

The token values mirror ``app/components/tokens.py``. Component-specific rules
are scoped to ``tm-*`` classes / ``data-*`` attributes emitted by
``app/components``.
"""

import streamlit as st

_CSS = """
<style>
  :root {
    --tone-neutral: #5b616e; --tone-warning: #8a5000; --tone-success: #0f6b3d;
    --tone-danger: #b3261e;  --tone-info: #1c5fb8;
    --accent-neutral: #5b616e; --accent-warning: #c77800; --accent-success: #1a8a52;
    --accent-danger: #b3261e;  --accent-info: #1c64f2;
    --focus-ring: #1c64f2;
  }

  /* ---- spacing: reclaim Streamlit's oversized default paddings ---------- */
  .block-container, [data-testid="stMainBlockContainer"] {
    padding-top: 1.6rem; padding-bottom: 2rem; max-width: 880px;
  }
  [data-testid="stSidebarUserContent"] { padding-top: 1.1rem; }
  [data-testid="stVerticalBlock"] { gap: 0.55rem; }
  [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] { gap: 0.2rem; }
  hr { margin: 0.5rem 0; }
  h1 { margin-bottom: 0.1rem; padding-top: 0; }
  [data-testid="stMainBlockContainer"] h2 {
    font-size: 1.15rem; padding-top: 0.4rem; margin-bottom: 0.1rem;
  }

  /* ---- accessibility -------------------------------------------------- */
  /* 2.4.7 Focus Visible */
  a:focus-visible, button:focus-visible, input:focus-visible,
  select:focus-visible, textarea:focus-visible,
  [role="radio"]:focus-visible, [role="button"]:focus-visible,
  [data-baseweb="input"] input:focus-visible {
    outline: 3px solid var(--focus-ring) !important;
    outline-offset: 2px !important; border-radius: 4px;
  }
  /* 2.5.5 Target Size */
  .stButton > button { min-height: 2.5rem; }
  /* 2.3.3 Reduced motion */
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      transition: none !important; animation: none !important;
      scroll-behavior: auto !important;
    }
  }
  /* the popover chevron leaks the ligature "expand_more" into the a11y name */
  button[data-testid="stPopoverButton"] span[data-testid="stIconMaterial"] { display: none; }

  /* ---- component: badge -------------------------------------------------- */
  .tm-badge {
    display: inline-block; padding: 0.05rem 0.55rem; border-radius: 999px;
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.02em;
    vertical-align: middle; margin-left: 0.4rem; color: #fff; white-space: nowrap;
    max-width: 16rem; overflow: hidden; text-overflow: ellipsis;
  }
  .tm-badge[data-tone="neutral"] { background: var(--tone-neutral); }
  .tm-badge[data-tone="warning"] { background: var(--tone-warning); }
  .tm-badge[data-tone="success"] { background: var(--tone-success); }
  .tm-badge[data-tone="danger"]  { background: var(--tone-danger); }
  .tm-badge[data-tone="info"]    { background: var(--tone-info); }

  /* ---- component: card -- coloured left edge + muted state --------------
     Keyed on the container's st-key-* class (card() builds it as
     "tmcard-<accent>[-muted]-<id>"), since this Streamlit paints the border
     straight onto stVerticalBlock (no BorderWrapper to hang :has() on). */
  [class*="st-key-tmcard-warning"] { border-left: 4px solid var(--accent-warning) !important; }
  [class*="st-key-tmcard-success"] { border-left: 4px solid var(--accent-success) !important; }
  [class*="st-key-tmcard-danger"]  { border-left: 4px solid var(--accent-danger) !important; }
  [class*="st-key-tmcard-info"]    { border-left: 4px solid var(--accent-info) !important; }
  [class*="st-key-tmcard"][class*="-muted-"] .tm-title,
  [class*="st-key-tmcard"][class*="-muted-"] .tm-desc { opacity: 0.6; }

  /* ---- task text ------------------------------------------------------- */
  .tm-title {
    font-weight: 600; overflow-wrap: anywhere;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  }
  .tm-title--done { text-decoration: line-through; }
  .tm-desc {
    color: inherit; opacity: 0.85; font-size: 0.9rem; margin-top: 0.1rem;
    display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; overflow: hidden;
  }
  .tm-dates { color: inherit; opacity: 0.78; font-size: 0.76rem; margin-top: 0.15rem; }

  /* ---- component: chip ------------------------------------------------- */
  .st-key-tm-chips button {
    min-height: 1.9rem; padding: 0 0.7rem; border-radius: 999px;
    font-size: 0.8rem; font-weight: 600; white-space: nowrap;
  }
  .tm-chip--static {
    display: inline-block; padding: 0.15rem 0.7rem; border-radius: 999px;
    font-size: 0.8rem; font-weight: 600; background: rgba(128,128,128,0.18);
  }

  /* ---- component: empty_state --------------------------------------- */
  .tm-empty { text-align: center; padding: 1.4rem 0.5rem; }
  .tm-empty__icon  { font-size: 1.9rem; line-height: 1; }
  .tm-empty__title { font-weight: 600; margin-top: 0.4rem; }
  .tm-empty__body  { opacity: 0.75; font-size: 0.9rem; margin-top: 0.15rem; }

  /* ---- component: pager --------------------------------------------- */
  .tm-pageno { text-align: center; font-size: 0.85rem; opacity: 0.75; padding-top: 0.5rem; }

  /* ---- responsive --------------------------------------------------- */
  @media (max-width: 640px) {
    .block-container, [data-testid="stMainBlockContainer"] { padding-left: 0.8rem; padding-right: 0.8rem; }
    .tm-badge { max-width: 9rem; }
  }
</style>
"""


def inject_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
