CSS_AUTH = """
<style>
.auth-shell {{
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 48px 0 24px;
}}
.auth-top {{
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}}
.auth-logo {{
    width: 120px;
    height: auto;
    margin-bottom: 8px;
}}
.auth-logo-icon {{
    width: 56px;
    height: 56px;
    border-radius: 14px;
    background: linear-gradient(135deg, {NAVY}, {ORANGE});
    display: flex;
    align-items: center;
    justify-content: center;
    color: {WHITE};
    font-size: 26px;
    margin-bottom: 8px;
    box-shadow: 0 4px 14px rgba(249,120,56,.3);
}}
.auth-brand {{
    font-size: 22px !important;
    font-weight: 700 !important;
    color: {NAVY} !important;
    letter-spacing: -.02em;
    text-align: center;
    display: block;
}}
.auth-brand-sub {{
    font-size: 13px !important;
    color: {MUTED} !important;
    margin-bottom: 12px;
    text-align: center;
    display: block;
}}
.auth-card {{
    max-width: 400px;
    margin: 0 auto;
    background: {WHITE};
    border-radius: 12px;
    border: 0.5px solid {BORDER};
    border-top: 3px solid {ORANGE};
    padding: 28px 28px 20px;
    box-shadow: 0 2px 12px rgba(0,9,39,.06);
}}
.auth-footer {{
    text-align: center;
    font-size: 12px;
    color: {MUTED};
    margin-top: 8px;
}}

/* ── Login form overrides ── */
[data-testid="stForm"] {{
    max-width: 400px;
    margin: 0 auto;
    background: {WHITE};
    border-radius: 12px;
    border: 0.5px solid {BORDER};
    border-top: 3px solid {ORANGE};
    padding: 28px 28px 20px;
    box-shadow: 0 2px 12px rgba(0,9,39,.06);
}}
div[data-testid="stFormSubmitButton"] > button {{
    background-color: {ORANGE} !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    height: 48px;
    font-weight: 600;
    transition: all 0.2s ease;
}}
div[data-testid="stFormSubmitButton"] > button:hover {{
    background-color: #e86a2b !important;
    color: white !important;
}}
div[data-testid="stFormSubmitButton"] > button:active {{
    background-color: {NAVY} !important;
}}
</style>
"""
