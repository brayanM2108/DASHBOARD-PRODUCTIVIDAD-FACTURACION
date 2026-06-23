CSS_GLOBAL = """
<style>
/* ── Fondo general ── */
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {{
    background: {BG} !important;
}}
[data-testid="stHeader"] {{
    background: transparent !important;
    border-bottom: none !important;
    height: 0 !important;
    min-height: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
    overflow: hidden !important;
    visibility: hidden !important;
    display: none !important;
}}

/* ── Padding del contenedor principal (reemplaza .main-content-area) ── */
[data-testid="stMainBlockContainer"] {{
    padding: 12px 32px 24px !important;
    margin-top: 0 !important;
}}

/* ── Sidebar header y botón de colapso ocultos ── */
[data-testid="stSidebarHeader"],
[data-testid="stSidebarCollapseButton"],
[data-testid="baseButton-headerNoPadding"],
[data-testid="stExpandSidebarButton"] {{
    display: none !important;
}}

/* ── Título fijo de cada tab ── */
.g-tab-title {{
    font-size: 22px !important;
    font-weight: 700 !important;
    color: {NAVY} !important;
    margin-bottom: 12px !important;
    padding-bottom: 8px !important;
    border-bottom: 1px solid {BORDER} !important;
    letter-spacing: -0.02em !important;
}}

/* ── Gap entre horizontal blocks ── */
[data-testid="stMainBlockContainer"] .stHorizontalBlock {{
    gap: 16px !important;
}}

/* ── Scrollbar sutil ── */
::-webkit-scrollbar {{ width: 6px; height: 6px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{
    background: {BORDER};
    border-radius: 3px;
}}
::-webkit-scrollbar-thumb:hover {{ background: {MUTED}; }}

/* ── Tipografía base ── */
html, body, [class*="css"] {{
    font-family: "Segoe UI", -apple-system, BlinkMacSystemFont, sans-serif !important;
    color: {TEXT};
}}

/* ─ Títulos con acento izquierdo ── */
h1 {{ color: {NAVY} !important; font-weight: 700 !important; }}
h2 {{ color: {NAVY} !important; font-weight: 600 !important; }}
h3 {{
    color: {NAVY} !important;
    font-weight: 600 !important;
    border-left: 3px solid {ORANGE} !important;
    padding-left: 10px !important;
}}

/* ── Ocultar contenedores de sentinel markers ── */
.element-container:has(#sb-logout-marker),
.element-container:has(#chart-grid-start) {{
    height: 0 !important;
    overflow: hidden !important;
    margin: 0 !important;
    padding: 0 !important;
    border: none !important;
}}
</style>
"""
