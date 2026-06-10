CSS_TABLES = """
<style>
/* ── Encabezado de tabla ── */
[data-testid="stDataFrame"] thead th {{
    background: {NAVY} !important;
    color: {WHITE} !important;
    font-size: 11px !important;
    text-transform: uppercase !important;
    letter-spacing: .04em !important;
    font-weight: 500 !important;
    padding: 8px 12px !important;
}}

/* ── Filas hover ── */
[data-testid="stDataFrame"] tbody tr:hover td {{
    background: {BLUE_LIGHT} !important;
}}

/* ── Borde del contenedor ── */
[data-testid="stDataFrame"] {{
    border: 0.5px solid {BORDER} !important;
    border-radius: 10px !important;
    overflow: hidden !important;
}}
</style>
"""
