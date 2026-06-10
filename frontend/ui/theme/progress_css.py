CSS_PROGRESS = """
<style>
[data-testid="stSpinner"] > div {{
    border-top-color: {ORANGE} !important;
}}
[data-testid="stProgressBar"] > div {{
    background: {BLUE_LIGHT} !important;
    border-radius: 4px !important;
}}
[data-testid="stProgressBar"] > div > div {{
    background: linear-gradient(90deg, {BLUE}, {ORANGE}) !important;
    border-radius: 4px !important;
}}
</style>
"""
