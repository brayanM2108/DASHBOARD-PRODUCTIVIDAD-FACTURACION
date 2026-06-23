CSS_GLOBAL_FILTERS = """
<style>
/* ══════════════════════════════════════════════════════════════════
   Global Filters — Goleman IPS Theme
   Scope: .st-key-gf_bar (st.container key)
   ══════════════════════════════════════════════════════════════════ */

/* ── Card container ── */
.st-key-gf_bar [data-testid="stHorizontalBlock"] {{
    background: {WHITE} !important;
    border: 0.5px solid {BORDER} !important;
    border-left: 3px solid {BLUE} !important;
    border-radius: 10px !important;
    padding: 16px 18px !important;
    margin: 0 0 10px !important;
    box-shadow: 0 1px 4px rgba(0,9,39,.04) !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] > div {{
    align-items: flex-end !important;
}}

/* ── Labels (uppercase, Goleman style) ── */
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stDateInput"] > label,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stDateInput"] p,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stSelectbox"] > label,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stSelectbox"] p,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stMultiSelect"] > label,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stMultiSelect"] p {{
    font-size: 11px !important;
    color: {MUTED} !important;
    font-weight: 500 !important;
    margin-bottom: 4px !important;
    letter-spacing: .04em !important;
    text-transform: uppercase !important;
}}

/* ── Neutralizar wrappers Streamlit (Emotion CSS-in-JS) ── */
.st-key-gf_bar [data-testid="stDateInput"]:focus-within,
.st-key-gf_bar [data-testid="stDateInput"] *:focus-within:not(input),
.st-key-gf_bar [data-testid="stDateInput"]:focus-visible,
.st-key-gf_bar [data-testid="stDateInput"] *:focus-visible:not(input),
.st-key-gf_bar [data-testid="stSelectbox"]:focus-within,
.st-key-gf_bar [data-testid="stSelectbox"] *:focus-within,
.st-key-gf_bar [data-testid="stSelectbox"]:focus-visible,
.st-key-gf_bar [data-testid="stSelectbox"] *:focus-visible,
.st-key-gf_bar [data-testid="stMultiSelect"]:focus-within,
.st-key-gf_bar [data-testid="stMultiSelect"] *:focus-within,
.st-key-gf_bar [data-testid="stMultiSelect"]:focus-visible,
.st-key-gf_bar [data-testid="stMultiSelect"] *:focus-visible,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stDateInput"]:focus-within,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stDateInput"] *:focus-within:not(input),
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stDateInput"]:focus-visible,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stDateInput"] *:focus-visible:not(input),
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stSelectbox"]:focus-within,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stSelectbox"] *:focus-within,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stSelectbox"]:focus-visible,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stSelectbox"] *:focus-visible,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stMultiSelect"]:focus-within,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stMultiSelect"] *:focus-within,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stMultiSelect"]:focus-visible,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stMultiSelect"] *:focus-visible {{
    box-shadow: none !important;
    outline: none !important;
    border-color: inherit !important;
}}

/* ── Date inputs ── */
.st-key-gf_bar [data-testid="stDateInput"] {{
    margin-bottom: 0 !important;
}}
.st-key-gf_bar [data-testid="stDateInput"] .st-df {{
    padding-right: 0 !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stDateInput"] input,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stDateInput"] input[type="text"] {{
    background: {WHITE} !important;
    border: 0.5px solid {BORDER} !important;
    border-radius: 8px !important;
    color: {TEXT} !important;
    font-size: 13px !important;
    padding: 7px 12px !important;
    height: 38px !important;
    transition: border-color .15s ease, box-shadow .15s ease !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stDateInput"] input:hover,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stDateInput"] input[type="text"]:hover {{
    border-color: {BLUE} !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stDateInput"] input:focus,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stDateInput"] input[type="text"]:focus {{
    border-color: {BLUE} !important;
    box-shadow: 0 0 0 3px rgba(21,101,192,.1) !important;
    outline: none !important;
}}

/* ── Selectbox ── */
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stSelectbox"],
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stMultiSelect"] {{
    margin-bottom: 0 !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="select"],
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="select"] > div {{
    background: {WHITE} !important;
    border: 0.5px solid {BORDER} !important;
    border-radius: 8px !important;
    min-height: 38px !important;
    transition: border-color .15s ease, box-shadow .15s ease !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="select"]:hover,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="select"] > div:hover {{
    border-color: {BLUE} !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="select"]:focus-within,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="select"] > div:focus-within {{
    border-color: {BLUE} !important;
    box-shadow: 0 0 0 3px rgba(21,101,192,.1) !important;
    outline: none !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="select"] span,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="select"] [data-baseweb="select-highlight"] span {{
    color: {TEXT} !important;
    font-size: 13px !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="select"] svg {{
    fill: {MUTED} !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="select"] input {{
    color: {TEXT} !important;
    font-size: 13px !important;
}}

/* ── Multiselect tags ── */
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stMultiSelect"] [data-baseweb="tag"],
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="tag"] {{
    background: {BLUE_LIGHT} !important;
    border-radius: 6px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    color: {NAVY} !important;
    padding: 2px 6px !important;
    margin: 2px !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stMultiSelect"] [data-baseweb="tag"] svg,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="tag"] svg {{
    fill: {MUTED} !important;
    cursor: pointer !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-testid="stMultiSelect"] [data-baseweb="tag"]:hover,
.st-key-gf_bar [data-testid="stHorizontalBlock"] [data-baseweb="tag"]:hover {{
    background: {SKY_LIGHT} !important;
}}

/* ── Calendar popover (Goleman navy style) ── */
.st-key-gf_bar [data-baseweb="calendar"],
.st-key-gf_bar [data-baseweb="calendar"] [data-baseweb="calendar-header"] {{
    background: {NAVY2} !important;
    border: 0.5px solid rgba(255,255,255,.1) !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,.3) !important;
}}
.st-key-gf_bar [data-baseweb="calendar"] * {{
    color: rgba(255,255,255,.8) !important;
}}
.st-key-gf_bar [data-baseweb="calendar"] button:hover {{
    background: rgba(249,120,56,.15) !important;
}}
.st-key-gf_bar [data-baseweb="calendar"] button[aria-selected="true"] {{
    background: {ORANGE} !important;
    color: {WHITE} !important;
    border-radius: 8px !important;
}}

/* ── Apply button (4th column) ── */
.st-key-gf_bar [data-testid="stHorizontalBlock"] > div:nth-child(4) [data-testid="stButton"] {{
    padding-top: 19px !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] button[kind="primary"] {{
    background: {NAVY} !important;
    color: {WHITE} !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    padding: 0 20px !important;
    height: 38px !important;
    width: 100% !important;
    white-space: nowrap !important;
    transition: background .15s ease !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] button[kind="primary"]:hover {{
    background: {NAVY2} !important;
}}
.st-key-gf_bar [data-testid="stHorizontalBlock"] button[kind="primary"]:active {{
    transform: scale(.98) !important;
}}
</style>
"""
