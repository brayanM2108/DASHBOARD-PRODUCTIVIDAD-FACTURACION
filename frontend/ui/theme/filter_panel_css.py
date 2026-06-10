CSS_FILTER_PANEL = """
<style>
[data-testid="stSidebar"] .g-filter-header {{
    display: flex !important;
    align-items: center !important;
    gap: 6px !important;
    font-size: 9px !important;
    font-weight: 500 !important;
    color: rgba(255,255,255,.3) !important;
    letter-spacing: .08em !important;
    text-transform: uppercase !important;
    padding: 12px 14px 8px !important;
}}
[data-testid="stSidebar"] .g-filter-header span {{
    font-size: 11px !important;
}}

/* --- Date inputs --- */
[data-testid="stSidebar"] [data-testid="stDateInput"] {{
    margin-bottom: 6px !important;
}}
[data-testid="stSidebar"] [data-testid="stDateInput"] > label,
[data-testid="stSidebar"] [data-testid="stDateInput"] p {{
    font-size: 10px !important;
    color: rgba(255,255,255,.4) !important;
    font-weight: 400 !important;
    margin-bottom: 2px !important;
}}
[data-testid="stSidebar"] [data-testid="stDateInput"] input {{
    background: rgba(255,255,255,.06) !important;
    border: 0.5px solid rgba(255,255,255,.10) !important;
    border-radius: 8px !important;
    color: {WHITE} !important;
    font-size: 12px !important;
    padding: 6px 10px !important;
    height: 34px !important;
    transition: border-color .2s ease, box-shadow .2s ease !important;
}}
[data-testid="stSidebar"] [data-testid="stDateInput"] input:focus {{
    border-color: {BLUE} !important;
    box-shadow: 0 0 0 2px rgba(21,101,192,.2) !important;
}}

/* --- Selectbox (user filter) --- */
[data-testid="stSidebar"] [data-testid="stSelectbox"] {{
    margin-bottom: 6px !important;
}}
[data-testid="stSidebar"] [data-testid="stSelectbox"] > label,
[data-testid="stSidebar"] [data-testid="stSelectbox"] p {{
    font-size: 10px !important;
    color: rgba(255,255,255,.4) !important;
    font-weight: 400 !important;
    margin-bottom: 2px !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div {{
    background: rgba(255,255,255,.06) !important;
    border: 0.5px solid rgba(255,255,255,.10) !important;
    border-radius: 8px !important;
    min-height: 34px !important;
    transition: border-color .2s ease, box-shadow .2s ease !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div:hover {{
    border-color: rgba(255,255,255,.2) !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] > div:focus-within {{
    border-color: {BLUE} !important;
    box-shadow: 0 0 0 2px rgba(21,101,192,.2) !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] span {{
    color: {WHITE} !important;
    font-size: 12px !important;
}}
[data-testid="stSidebar"] [data-baseweb="select"] svg {{
    fill: rgba(255,255,255,.3) !important;
}}

/* --- Calendar popover --- */
[data-testid="stSidebar"] [data-baseweb="calendar"] {{
    background: {NAVY2} !important;
    border: 0.5px solid rgba(255,255,255,.1) !important;
    border-radius: 10px !important;
    box-shadow: 0 8px 24px rgba(0,0,0,.3) !important;
}}
[data-testid="stSidebar"] [data-baseweb="calendar"] * {{
    color: rgba(255,255,255,.8) !important;
}}
[data-testid="stSidebar"] [data-baseweb="calendar"] button:hover {{
    background: rgba(249,120,56,.15) !important;
}}
[data-testid="stSidebar"] [data-baseweb="calendar"] button[aria-selected="true"] {{
    background: {ORANGE} !important;
    color: {WHITE} !important;
}}

/* --- Filter section spacing --- */
[data-testid="stSidebar"] .g-filter-section {{
    padding: 0 12px !important;
}}
</style>
"""
