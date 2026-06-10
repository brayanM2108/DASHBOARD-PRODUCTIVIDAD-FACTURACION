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

[data-testid="stSidebar"] .g-nav-item {{
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    padding: 8px 14px 8px 12px !important;
    margin: 0 8px 2px !important;
    border-radius: 8px !important;
    cursor: pointer !important;
    position: relative !important;
    transition: all .18s ease !important;
    border-left: 3px solid transparent !important;
}}
[data-testid="stSidebar"] .g-nav-item:hover {{
    background: rgba(255,255,255,.07) !important;
}}
[data-testid="stSidebar"] .g-nav-item--active {{
    background: rgba(255,255,255,.08) !important;
    border-left-color: {ORANGE} !important;
}}
[data-testid="stSidebar"] .g-nav-item--active:hover {{
    background: rgba(255,255,255,.10) !important;
}}

[data-testid="stSidebar"] .g-nav-icon {{
    font-size: 15px !important;
    width: 20px !important;
    text-align: center !important;
    flex-shrink: 0 !important;
    line-height: 1 !important;
}}
[data-testid="stSidebar"] .g-nav-text {{
    font-size: 12.5px !important;
    color: rgba(255,255,255,.7) !important;
    flex: 1 !important;
    font-weight: 400 !important;
    line-height: 1.3 !important;
}}
[data-testid="stSidebar"] .g-nav-item--active .g-nav-text {{
    color: {WHITE} !important;
    font-weight: 500 !important;
}}
[data-testid="stSidebar"] .g-nav-item:hover .g-nav-text {{
    color: rgba(255,255,255,.9) !important;
}}
</style>
"""
