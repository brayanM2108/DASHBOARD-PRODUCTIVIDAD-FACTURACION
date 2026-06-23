CSS_HELPERS = """
<style>
.g-section-title {{
    color: {BLUE};
    font-size: 12px;
    font-weight: 600;
    letter-spacing: .05em;
    text-transform: uppercase;
    margin-bottom: 12px;
}}
.g-chart-card {{
    background: {WHITE};
    border-radius: 10px;
    border: 0.5px solid {BORDER};
    padding: 16px;
}}
.g-muted-note {{
    color: {MUTED};
    font-size: 11px;
}}

/* -- Chart card with orange left accent (Procesos Adm.) -- */
.g-chart-card-accent {{
    background: {WHITE};
    border: 0.5px solid {BORDER};
    border-left: 3px solid {ORANGE};
    border-radius: 10px;
    padding: 16px 18px;
    box-shadow: 0 1px 4px rgba(0,9,39,.04);
}}
</style>
"""
