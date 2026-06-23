CSS_NAVIGATION = """
<style>
[data-testid="stSidebar"] .g-nav-label {{
    font-size: 9px !important;
    font-weight: 500 !important;
    color: rgba(255,255,255,.3) !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    padding: 16px 14px 8px !important;
}}

/* ── Nav wrapper: posiciona el botón invisible encima del item visual ── */
[data-testid="stSidebar"] .g-nav-wrapper {{
    position: relative !important;
    margin: 2px 8px !important;
}}

/* ── Nav item visual: icono + texto ── */
[data-testid="stSidebar"] .g-nav-item {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 8px 14px !important;
    border-radius: 8px !important;
    color: rgba(255,255,255,.7) !important;
    font-size: 12.5px !important;
    font-weight: 400 !important;
    transition: all .18s ease !important;
    border-left: 3px solid transparent !important;
    user-select: none !important;
    pointer-events: none !important;
}}
[data-testid="stSidebar"] .g-nav-wrapper:hover .g-nav-item {{
    background: rgba(255,255,255,.07) !important;
    color: rgba(255,255,255,.9) !important;
}}
[data-testid="stSidebar"] .g-nav-wrapper:active .g-nav-item {{
    background: rgba(255,255,255,.10) !important;
    border-left-color: {ORANGE} !important;
}}
[data-testid="stSidebar"] .g-nav-item img {{
    flex-shrink: 0 !important;
    display: block !important;
    width: 18px !important;
    height: 18px !important;
}}

/* ── Botón invisible superpuesto ── */
[data-testid="stSidebar"] .g-nav-wrapper .stButton {{
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    width: 100% !important;
    height: 100% !important;
    margin: 0 !important;
    padding: 0 !important;
    z-index: 2 !important;
}}
[data-testid="stSidebar"] .g-nav-wrapper button {{
    width: 100% !important;
    height: 100% !important;
    min-height: 36px !important;
    background: transparent !important;
    border: none !important;
    cursor: pointer !important;
    opacity: 0 !important;
    padding: 0 !important;
    margin: 0 !important;
}}

/* ── Botón expandir sidebar oculto ── */
[data-testid="stSidebarCollapseButton"],
[data-testid="baseButton-headerNoPadding"],
[data-testid="stExpandSidebarButton"] {{
    display: none !important;
}}
</style>
"""
