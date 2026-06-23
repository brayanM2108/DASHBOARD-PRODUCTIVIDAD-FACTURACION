CSS_FORMS = """
<style>
/* ── Neutralizar wrappers Streamlit (Emotion CSS-in-JS) ── */
[data-testid="stTextInput"]:focus-within,
[data-testid="stTextInput"] *:focus-within:not(input),
[data-testid="stTextInput"]:focus-visible,
[data-testid="stTextInput"] *:focus-visible:not(input),
[data-testid="stTextInput"]:focus:not(input),
[data-testid="stTextInput"] *:focus:not(input),
[data-testid="stSelectbox"]:focus-within,
[data-testid="stSelectbox"] *:focus-within,
[data-testid="stSelectbox"]:focus-visible,
[data-testid="stSelectbox"] *:focus-visible,
[data-testid="stMultiSelect"]:focus-within,
[data-testid="stMultiSelect"] *:focus-within,
[data-testid="stMultiSelect"]:focus-visible,
[data-testid="stMultiSelect"] *:focus-visible,
[data-testid="stDateInput"]:focus-within,
[data-testid="stDateInput"] *:focus-within:not(input),
[data-testid="stDateInput"]:focus-visible,
[data-testid="stDateInput"] *:focus-visible:not(input) {{
    box-shadow: none !important;
    outline: none !important;
    border-color: transparent !important;
}}

/* ── Text input ── */
[data-testid="stTextInput"] input,
[data-testid="stNumberInput"] input {{
    border: 0.5px solid {BORDER} !important;
    border-radius: 8px !important;
    background: {WHITE} !important;
    color: {TEXT} !important;
    font-size: 13px !important;
}}
[data-testid="stTextInput"] input:focus,
[data-testid="stNumberInput"] input:focus {{
    border-color: {BLUE} !important;
    box-shadow: 0 0 0 3px rgba(21,101,192,.1) !important;
    outline: none !important;
}}

/* ── Selectbox ── */
[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
    border: 0.5px solid {BORDER} !important;
    border-radius: 8px !important;
    background: {WHITE} !important;
}}
[data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within {{
    border-color: {BLUE} !important;
    box-shadow: 0 0 0 3px rgba(21,101,192,.1) !important;
    outline: none !important;
}}

/* ── Date input ── */
[data-testid="stDateInput"] input {{
    border: 0.5px solid {BORDER} !important;
    border-radius: 8px !important;
    background: {WHITE} !important;
}}

/* ── Textarea ── */
[data-testid="stTextArea"] textarea {{
    border: 0.5px solid {BORDER} !important;
    border-radius: 8px !important;
    background: {WHITE} !important;
}}
[data-testid="stTextArea"] textarea:focus {{
    border-color: {BLUE} !important;
    box-shadow: 0 0 0 3px rgba(21,101,192,.1) !important;
    outline: none !important;
}}

/* ── File uploader ── */
[data-testid="stFileUploader"] {{
    border: 1.5px dashed {BORDER} !important;
    border-radius: 10px !important;
    background: {BG2} !important;
}}
[data-testid="stFileUploader"]:hover {{
    border-color: {ORANGE} !important;
    background: {ORANGE_LIGHT} !important;
}}
</style>
"""
