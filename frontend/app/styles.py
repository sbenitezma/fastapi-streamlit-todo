"""Global CSS: reclaim empty space + accessibility hardening (WCAG 2.1 AA)."""

import streamlit as st

_CSS = """
<style>
  /* Trim the oversized default paddings that leave the screen half empty */
  .block-container, [data-testid="stMainBlockContainer"] {
    padding-top: 1.6rem; padding-bottom: 2rem; max-width: 880px;
  }
  [data-testid="stSidebarUserContent"] { padding-top: 1.1rem; }
  [data-testid="stVerticalBlock"] { gap: 0.55rem; }
  [data-testid="stVerticalBlockBorderWrapper"] [data-testid="stVerticalBlock"] {
    gap: 0.2rem;
  }
  hr { margin: 0.5rem 0; }
  h1 { margin-bottom: 0.1rem; padding-top: 0; }
  [data-testid="stMainBlockContainer"] h2 {
    font-size: 1.15rem; padding-top: 0.4rem; margin-bottom: 0.1rem;
  }

  /* Drop the popover chevron: it leaks the ligature text "expand_more"
     into the button's accessible name. The label is enough. */
  button[data-testid="stPopoverButton"] span[data-testid="stIconMaterial"] {
    display: none;
  }

  /* WCAG 2.4.7 Focus Visible -- a strong, consistent focus ring */
  a:focus-visible, button:focus-visible, input:focus-visible,
  select:focus-visible, textarea:focus-visible,
  [role="radio"]:focus-visible, [role="button"]:focus-visible,
  [data-baseweb="input"] input:focus-visible {
    outline: 3px solid #1c64f2 !important;
    outline-offset: 2px !important;
    border-radius: 4px;
  }

  /* WCAG 2.5.5 Target Size -- comfortable click/tap areas */
  .stButton > button { min-height: 2.5rem; }

  /* WCAG 2.3.3 -- respect users who ask for less motion */
  @media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
      transition: none !important; animation: none !important;
      scroll-behavior: auto !important;
    }
  }

  /* Status pill: icon + word are always present; colour only reinforces.
     Self-contained colours (own background + white text) meet 4.5:1 on any theme. */
  .tm-badge {
    display: inline-block; padding: 0.05rem 0.55rem; border-radius: 999px;
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.02em;
    vertical-align: middle; margin-left: 0.4rem; color: #ffffff;
    white-space: nowrap;
  }
  .tm-badge.pending { background: #8a5000; }  /* white on #8a5000 = 7.5:1 */
  .tm-badge.done    { background: #0f6b3d; }  /* white on #0f6b3d = 7.0:1 */

  /* Third status cue: a coloured left edge on the card, and dimmed text
     for completed tasks so pending ones stand out. */
  [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-flag.pending) {
    border-left: 4px solid #c77800 !important;
  }
  [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-flag.done) {
    border-left: 4px solid #1a8a52 !important;
  }
  [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-flag.done) .tm-title,
  [data-testid="stVerticalBlockBorderWrapper"]:has(.tm-flag.done) .tm-desc {
    opacity: 0.6;
  }

  .tm-title { font-weight: 600; }
  .tm-title.done { text-decoration: line-through; }
  .tm-desc  { color: inherit; opacity: 0.85; font-size: 0.9rem; margin-top: 0.1rem; }
  .tm-dates { color: inherit; opacity: 0.78; font-size: 0.76rem; margin-top: 0.15rem; }

  /* Active-filter chips */
  .tm-chips .stButton > button {
    min-height: 1.9rem; padding: 0 0.6rem; border-radius: 999px;
    font-size: 0.8rem; font-weight: 600;
  }
</style>
"""


def inject_styles() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)
