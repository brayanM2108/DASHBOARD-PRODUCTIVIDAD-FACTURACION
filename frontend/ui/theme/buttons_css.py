CSS_BUTTONS = """
<style>
/* ── Botón primario ── */
[data-testid="stButton"] > button[kind="primary"],
[data-testid="stFormSubmitButton"] > button {{
    background: {NAVY} !important;
    color: {WHITE} !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
    padding: 8px 18px !important;
    transition: background .15s !important;
}}
[data-testid="stButton"] > button[kind="primary"]:hover {{
    background: {NAVY2} !important;
}}

/* ── Botón secundario ── */
[data-testid="stButton"] > button[kind="secondary"] {{
    background: transparent !important;
    color: {NAVY} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 8px !important;
    font-weight: 400 !important;
}}
[data-testid="stButton"] > button[kind="secondary"]:hover {{
    border-color: {BLUE} !important;
    color: {BLUE} !important;
    background: {BLUE_LIGHT} !important;
}}

/* ── Botón de descarga ── */
[data-testid="stDownloadButton"] > button {{
    background: transparent !important;
    color: {ORANGE} !important;
    border: 1.5px solid {ORANGE} !important;
    border-radius: 8px !important;
    font-weight: 500 !important;
}}
[data-testid="stDownloadButton"] > button:hover {{
    background: {ORANGE_LIGHT} !important;
}}
</style>
"""
