CSS_EXPANDERS = """
<style>
[data-testid="stExpander"] {{
    border: 0.5px solid {BORDER} !important;
    border-radius: 10px !important;
    background: {WHITE} !important;
    overflow: hidden !important;
}}
[data-testid="stExpander"] summary {{
    background: {BG2} !important;
    padding: 10px 14px !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    color: {NAVY} !important;
}}
[data-testid="stExpander"] summary:hover {{
    background: {BLUE_LIGHT} !important;
}}
[data-testid="stExpander"] summary svg {{
    color: {ORANGE} !important;
}}
</style>
"""
