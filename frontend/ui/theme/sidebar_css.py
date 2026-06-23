CSS_SIDEBAR = """
<style>
/* ── Asegurar que el sidebar sea visible y fijo ── */
[data-testid="stSidebar"] {{
    display: flex !important;
    visibility: visible !important;
    position: relative !important;
    transform: none !important;
    background: {NAVY} !important;
    border-right: 0.5px solid rgba(255,255,255,.06) !important;
    width: 280px !important;
    min-width: 280px !important;
    max-width: 280px !important;
    overflow: hidden !important;
    z-index: 999990 !important;
}}

/* ── Contenedor interno del sidebar ── */
[data-testid="stSidebar"] > div:first-child {{
    padding: 0 !important;
    width: 100% !important;
    overflow-y: auto !important;
}}
[data-testid="stSidebar"] > div:first-child > div:first-child {{
    padding: 0 !important;
    width: 100% !important;
}}

/* ── Logo centrado ── */
[data-testid="stSidebar"] .g-sidebar-logo {{
    text-align: center !important;
    padding: 24px 18px 18px !important;
}}
[data-testid="stSidebar"] .g-sidebar-logo img {{
    width: 138px !important;
    height: auto !important;
    display: inline-block !important;
}}

/* ── Botón de colapso y resizer ocultos ── */
[data-testid="stSidebarCollapseButton"],
[data-testid="baseButton-headerNoPadding"],
[data-testid="stExpandSidebarButton"],
[data-testid="stSidebar"] [class*="Resize"],
[data-testid="stSidebar"] [class*="resize"] {{
    display: none !important;
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

/* ─ Streamlit native overrides ── */
/* Excluir botones de navegación (tienen clase st-key-nav_*) */
[data-testid="stSidebar"] .stButton:not([class*="st-key-nav_"]) {{
    width: 100%;
}}
</style>
"""
