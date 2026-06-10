CSS_GLOBAL = """
<style>
/* ── Fondo general ── */
[data-testid="stAppViewContainer"],
[data-testid="stMain"] {{
    background: {BG} !important;
}}
[data-testid="stHeader"] {{
    background: {NAVY} !important;
    border-bottom: none !important;
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

/* ── Títulos con acento izquierdo ── */
h1 {{ color: {NAVY} !important; font-weight: 700 !important; }}
h2 {{ color: {NAVY} !important; font-weight: 600 !important; }}
h3 {{
    color: {NAVY} !important;
    font-weight: 600 !important;
    border-left: 3px solid {ORANGE} !important;
    padding-left: 10px !important;
}}

/* ── Franja decorativa superior ── */
[data-testid="stAppViewContainer"]::before {{
    content: '';
    display: block;
    height: 3px;
    background: linear-gradient(90deg, {NAVY}, {BLUE} 40%, {ORANGE});
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 9999;
}}
</style>
"""
