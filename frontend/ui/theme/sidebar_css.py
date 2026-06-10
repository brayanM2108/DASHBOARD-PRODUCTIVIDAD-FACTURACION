CSS_SIDEBAR = """
<style>
/* ── Fondo sidebar ── */
[data-testid="stSidebar"] {{
    background: {NAVY} !important;
    border-right: none !important;
}}
[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
}}

/* ── Botón de colapso ── */
[data-testid="stSidebarCollapseButton"] {{
    background: rgba(255,255,255,.05) !important;
    border: 0.5px solid rgba(255,255,255,.08) !important;
    border-radius: 6px !important;
    transition: background .2s ease !important;
}}
[data-testid="stSidebarCollapseButton"]:hover {{
    background: rgba(255,255,255,.1) !important;
}}
[data-testid="stSidebarCollapseButton"] svg {{
    color: rgba(255,255,255,.35) !important;
}}

/* ── Textos generales ── */
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span {{
    color: rgba(255,255,255,.75) !important;
}}
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {{
    color: {WHITE} !important;
    border: none !important;
    padding: 0 !important;
}}

/* ── Labels generales ── */
[data-testid="stSidebar"] label {{
    color: rgba(255,255,255,.4) !important;
    font-weight: 400 !important;
}}

/* ── Dividers ── */
[data-testid="stSidebar"] hr {{
    border: none !important;
    border-top: 0.5px solid rgba(255,255,255,.06) !important;
    margin: 4px 12px !important;
    opacity: 0 !important;
}}

/* ── Streamlit native overrides ── */
[data-testid="stSidebar"] .stButton {{
    width: 100%;
}}
[data-testid="stSidebar"] div:has(> [data-testid="stDateInput"]) {{
    padding: 0 !important;
}}
[data-testid="stSidebar"] div:has(> [data-testid="stSelectbox"]) {{
    padding: 0 !important;
}}
</style>
"""
