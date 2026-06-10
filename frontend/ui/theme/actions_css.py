CSS_ACTIONS = """
<style>
[data-testid="stSidebar"] .g-actions-label {{
    font-size: 9px !important;
    font-weight: 500 !important;
    color: rgba(255,255,255,.3) !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    padding: 16px 14px 8px !important;
}}

/* ─ Primary button in sidebar (Aplicar filtros, Sí) ── */
[data-testid="stSidebar"] button[kind="primary"] {{
    background: {NAVY2} !important;
    color: {WHITE} !important;
    border: none !important;
    border-radius: 8px !important;
    font-size: 12.5px !important;
    font-weight: 500 !important;
    padding: 0 16px !important;
    height: 36px !important;
    width: 100% !important;
    transition: all .2s ease !important;
    letter-spacing: .01em !important;
}}
[data-testid="stSidebar"] button[kind="primary"]:hover {{
    background: #1a3a7a !important;
    box-shadow: 0 2px 12px rgba(13,43,94,.3) !important;
}}
[data-testid="stSidebar"] button[kind="primary"]:active {{
    transform: scale(.98) !important;
}}

/* ── Ghost/outline buttons (Recargar, Limpiar, No, Cerrar sesión) ── */
[data-testid="stSidebar"] button:not([kind="primary"]) {{
    background: transparent !important;
    border: 0.5px solid rgba(255,255,255,.08) !important;
    border-radius: 8px !important;
    color: rgba(255,255,255,.5) !important;
    font-size: 11.5px !important;
    font-weight: 400 !important;
    padding: 0 12px !important;
    height: 34px !important;
    transition: all .2s ease !important;
    width: 100% !important;
}}
[data-testid="stSidebar"] button:not([kind="primary"]):hover {{
    border-color: rgba(255,255,255,.2) !important;
    color: rgba(255,255,255,.8) !important;
    background: rgba(255,255,255,.05) !important;
}}

/* ── Footer ── */
[data-testid="stSidebar"] .g-sidebar-footer {{
    padding: 16px 14px 12px !important;
    border-top: 0.5px solid rgba(255,255,255,.06) !important;
    margin-top: 8px !important;
}}
[data-testid="stSidebar"] .g-footer-row {{
    font-size: 9.5px !important;
    color: rgba(255,255,255,.18) !important;
    line-height: 1.9 !important;
    letter-spacing: .01em !important;
}}
[data-testid="stSidebar"] .g-footer-row span {{
    color: rgba(255,255,255,.12) !important;
}}

/* ─ Summary ── */
[data-testid="stSidebar"] .g-summary {{
    padding: 0 12px !important;
}}
[data-testid="stSidebar"] .g-summary-label {{
    font-size: 9px !important;
    font-weight: 500 !important;
    color: rgba(255,255,255,.3) !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    padding: 14px 2px 10px !important;
}}
[data-testid="stSidebar"] .g-summary-grid {{
    display: grid !important;
    grid-template-columns: 1fr 1fr !important;
    gap: 8px !important;
}}
[data-testid="stSidebar"] .g-summary-card {{
    background: rgba(255,255,255,.04) !important;
    border: 0.5px solid rgba(255,255,255,.06) !important;
    border-left: 2.5px solid {ORANGE} !important;
    border-radius: 8px !important;
    padding: 10px 12px !important;
    transition: background .2s ease !important;
}}
[data-testid="stSidebar"] .g-summary-card:hover {{
    background: rgba(255,255,255,.07) !important;
}}
[data-testid="stSidebar"] .g-summary-value {{
    font-size: 18px !important;
    font-weight: 500 !important;
    color: {WHITE} !important;
    line-height: 1.2 !important;
}}
[data-testid="stSidebar"] .g-summary-title {{
    font-size: 9.5px !important;
    color: rgba(255,255,255,.35) !important;
    margin-top: 2px !important;
    letter-spacing: .02em !important;
}}

/* ── Column gap override for action row ── */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {{
    padding: 0 12px !important;
    gap: 8px !important;
}}
</style>
"""
