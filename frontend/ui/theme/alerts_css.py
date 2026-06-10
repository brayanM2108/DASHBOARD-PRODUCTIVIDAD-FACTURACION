CSS_ALERTS = """
<style>
/* ── Info ── */
[data-testid="stAlert"][data-baseweb="notification"] {{
    border-radius: 10px !important;
    font-size: 13px !important;
}}
div[data-testid="stAlert"] > div[data-baseweb="notification"][kind="info"] {{
    background: {BLUE_LIGHT} !important;
    border-left: 3px solid {BLUE} !important;
    color: {NAVY2} !important;
}}
/* ── Success ── */
div[data-testid="stAlert"] > div[data-baseweb="notification"][kind="success"] {{
    background: {SUCCESS_LIGHT} !important;
    border-left: 3px solid {SUCCESS} !important;
}}
/* ── Warning ── */
div[data-testid="stAlert"] > div[data-baseweb="notification"][kind="warning"] {{
    background: {WARNING_LIGHT} !important;
    border-left: 3px solid {WARNING} !important;
}}
/* ── Error ── */
div[data-testid="stAlert"] > div[data-baseweb="notification"][kind="error"] {{
    background: {DANGER_LIGHT} !important;
    border-left: 3px solid {DANGER} !important;
}}
</style>
"""
