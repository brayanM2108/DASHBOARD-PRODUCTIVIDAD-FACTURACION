CSS_TABS = """
<style>
/* ── Contenedor de tabs ── */
[data-testid="stTabs"] [role="tablist"] {{
    background: {NAVY} !important;
    padding: 0 8px !important;
    border-radius: 0 !important;
    gap: 0 !important;
    border-bottom: none !important;
}}

/* ── Tab inactivo ── */
[data-testid="stTabs"] button[role="tab"] {{
    color: rgba(255,255,255,.45) !important;
    border-bottom: 2px solid transparent !important;
    border-radius: 0 !important;
    padding: 10px 16px !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    background: transparent !important;
    transition: color .15s !important;
}}
[data-testid="stTabs"] button[role="tab"]:hover {{
    color: rgba(255,255,255,.8) !important;
    background: rgba(255,255,255,.05) !important;
}}

/* ── Tab activo ── */
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {{
    color: {WHITE} !important;
    border-bottom: 2px solid {ORANGE} !important;
    font-weight: 500 !important;
    background: transparent !important;
}}

/* ── Área de contenido del tab ── */
[data-testid="stTabs"] [data-testid="stTabsContent"] {{
    background: {BG} !important;
    padding: 20px 0 0 !important;
    border: none !important;
}}
</style>
"""
