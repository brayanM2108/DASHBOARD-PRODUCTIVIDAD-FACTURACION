CSS_USER_CARD = """
<style>
[data-testid="stSidebar"] .g-user-card {{
    margin: 0 12px 16px !important;
    display: flex !important;
    align-items: center !important;
    gap: 10px !important;
    background: rgba(255,255,255,.06) !important;
    border: 0.5px solid rgba(255,255,255,.08) !important;
    border-radius: 12px !important;
    padding: 12px 14px !important;
    transition: background .2s ease !important;
}}
[data-testid="stSidebar"] .g-user-card:hover {{
    background: rgba(255,255,255,.09) !important;
}}

[data-testid="stSidebar"] .g-user-avatar {{
    width: 36px !important;
    height: 36px !important;
    border-radius: 50% !important;
    background: linear-gradient(135deg, {ORANGE}, #e86a2b) !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    color: {WHITE} !important;
    flex-shrink: 0 !important;
    letter-spacing: .02em !important;
    box-shadow: 0 2px 8px rgba(249,120,56,.25) !important;
}}

[data-testid="stSidebar"] .g-user-info {{
    flex: 1 !important;
    min-width: 0 !important;
}}
[data-testid="stSidebar"] .g-user-name {{
    color: {WHITE} !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    white-space: nowrap !important;
    overflow: hidden !important;
    text-overflow: ellipsis !important;
    line-height: 1.3 !important;
}}
[data-testid="stSidebar"] .g-user-role {{
    display: inline-flex !important;
    align-items: center !important;
    margin-top: 4px !important;
    padding: 1px 8px !important;
    border-radius: 20px !important;
    background: rgba(249,120,56,.15) !important;
    color: {ORANGE} !important;
    font-size: 9px !important;
    font-weight: 500 !important;
    letter-spacing: .03em !important;
    text-transform: uppercase !important;
}}
[data-testid="stSidebar"] .g-user-status {{
    width: 8px !important;
    height: 8px !important;
    border-radius: 50% !important;
    background: #4CAF50 !important;
    flex-shrink: 0 !important;
    box-shadow: 0 0 6px rgba(76,175,80,.4) !important;
}}
</style>
"""
