CSS_TABLES = """
<style>

/* ==========================================================
   GOLEMAN TABLES v2
   ========================================================== */

/* Contenedor */
[data-testid="stDataFrame"] {{
    background: {WHITE} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 14px !important;
    overflow: visible !important;
    box-shadow: 0 2px 8px rgba(0,9,39,.04);
}}

/* Wrapper interno */
[data-testid="stDataFrame"] > div {{
    border-radius: 14px !important;
    overflow: hidden !important;
}}

/* Header */
[data-testid="stDataFrame"] thead th {{
    background: {NAVY} !important;
    color: white !important;
    font-size: 12px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: .06em !important;
    border: none !important;
    height: 44px !important;
}}

/* Celdas */
[data-testid="stDataFrame"] td {{
    font-size: 13px !important;
    color: {TEXT} !important;
    border-bottom: 1px solid #EEF2F7 !important;
    border-left: none !important;
    border-right: none !important;
    height: 42px !important;
}}

/* Filas alternadas */
[data-testid="stDataFrame"] tbody tr:nth-child(even) td {{
    background: #FBFCFE !important;
}}

/* Hover */
[data-testid="stDataFrame"] tbody tr:hover td {{
    background: #F3F8FF !important;
    transition: .15s ease;
}}

/* Primera columna */
[data-testid="stDataFrame"] tbody td:first-child {{
    font-weight: 500 !important;
    color: {NAVY} !important;
}}

/* Scroll */
[data-testid="stDataFrame"] ::-webkit-scrollbar {{
    width: 8px;
    height: 8px;
}}
[data-testid="stDataFrame"] ::-webkit-scrollbar-track {{
    background: transparent;
}}
[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb {{
    background: #CBD5E1;
    border-radius: 10px;
}}
[data-testid="stDataFrame"] ::-webkit-scrollbar-thumb:hover {{
    background: #94A3B8;
}}

/* Elimina bordes verticales */
[data-testid="stDataFrame"] table {{
    border-collapse: collapse !important;
}}
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] td {{
    border-left: none !important;
    border-right: none !important;
}}

</style>
"""