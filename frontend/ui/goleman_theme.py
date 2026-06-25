"""
ui/goleman_theme.py

Orquestador del tema Goleman IPS para Streamlit.
Delega la paleta y cada bloque CSS en ui/theme/* para facilitar el mantenimiento.

Uso:
    from ui.goleman_theme import GolemanTheme
    GolemanTheme.inject()
"""

from .theme.palette import (
    NAVY, NAVY2, BLUE, BLUE_LIGHT, SKY, SKY_LIGHT,
    ORANGE, ORANGE_LIGHT, WHITE, BG, BG2,
    TEXT, MUTED, BORDER, BORDER2,
    SUCCESS, SUCCESS_LIGHT, DANGER, DANGER_LIGHT,
    WARNING, WARNING_LIGHT,
)
from .theme.global_css import CSS_GLOBAL
from .theme.tabs_css import CSS_TABS
from .theme.sidebar_css import CSS_SIDEBAR
from .theme.metrics_css import CSS_METRICS
from .theme.buttons_css import CSS_BUTTONS
from .theme.forms_css import CSS_FORMS
from .theme.tables_css import CSS_TABLES
from .theme.alerts_css import CSS_ALERTS
from .theme.expanders_css import CSS_EXPANDERS
from .theme.progress_css import CSS_PROGRESS
from .theme.auth_css import CSS_AUTH
from .theme.helpers_css import CSS_HELPERS
from .theme.global_filters_css import CSS_ADMIN_REPORT_CARDS, CSS_ADMIN_REPORT_FILTERS, CSS_GLOBAL_FILTERS
from .theme.user_card_css import CSS_USER_CARD
from .theme.navigation_css import CSS_NAVIGATION
from .theme.sidebar_badges_css import CSS_SIDEBAR_BADGES
from .theme.filter_panel_css import CSS_FILTER_PANEL
from .theme.actions_css import CSS_ACTIONS
from .theme import helpers


class GolemanTheme:
    NAVY          = NAVY
    NAVY2         = NAVY2
    BLUE          = BLUE
    BLUE_LIGHT    = BLUE_LIGHT
    SKY           = SKY
    SKY_LIGHT     = SKY_LIGHT
    ORANGE        = ORANGE
    ORANGE_LIGHT  = ORANGE_LIGHT

    WHITE         = WHITE
    BG            = BG
    BG2           = BG2

    TEXT          = TEXT
    MUTED         = MUTED
    BORDER        = BORDER
    BORDER2       = BORDER2

    SUCCESS       = SUCCESS
    SUCCESS_LIGHT = SUCCESS_LIGHT
    DANGER        = DANGER
    DANGER_LIGHT  = DANGER_LIGHT
    WARNING       = WARNING
    WARNING_LIGHT = WARNING_LIGHT

    _CSS_BLOCKS = {
        "global":      CSS_GLOBAL,
        "tabs":        CSS_TABS,
        "sidebar":     CSS_SIDEBAR,
        "metrics":     CSS_METRICS,
        "buttons":     CSS_BUTTONS,
        "inputs":      CSS_FORMS,
        "dataframes":  CSS_TABLES,
        "alerts":      CSS_ALERTS,
        "expanders":   CSS_EXPANDERS,
        "progress":    CSS_PROGRESS,
        "auth":        CSS_AUTH,
        "helpers":     CSS_HELPERS,
        "user_card":   CSS_USER_CARD,
        "navigation":  CSS_NAVIGATION,
        "badges":      CSS_SIDEBAR_BADGES,
        "filter_panel":   CSS_FILTER_PANEL,
        "global_filters": CSS_GLOBAL_FILTERS,
        "admin_report_filters": CSS_ADMIN_REPORT_FILTERS,
        "admin_report_cards": CSS_ADMIN_REPORT_CARDS,
        "actions":        CSS_ACTIONS,
    }

    @classmethod
    def _palette_dict(cls):
        return {k: v for k, v in vars(cls).items()
                if k == k.upper() and isinstance(v, str)}

    @classmethod
    def inject(cls, *, sidebar: bool = True, auth: bool = False) -> None:
        import streamlit as st

        blocks = [
            CSS_GLOBAL, CSS_TABS, CSS_METRICS, CSS_BUTTONS,
            CSS_FORMS, CSS_TABLES, CSS_ALERTS, CSS_EXPANDERS,
            CSS_PROGRESS, CSS_HELPERS, CSS_GLOBAL_FILTERS, CSS_ADMIN_REPORT_FILTERS, CSS_ADMIN_REPORT_CARDS,
        ]
        if sidebar:
            blocks.extend([
                CSS_SIDEBAR, CSS_USER_CARD, CSS_NAVIGATION,
                CSS_SIDEBAR_BADGES, CSS_FILTER_PANEL, CSS_ACTIONS,
            ])
        if auth:
            blocks.append(CSS_AUTH)

        palette = cls._palette_dict()
        css = "\n".join(b.format_map(palette) for b in blocks)
        st.markdown(css, unsafe_allow_html=True)

    @classmethod
    def inject_sidebar(cls) -> None:
        import streamlit as st
        palette = cls._palette_dict()
        blocks = [
            CSS_SIDEBAR, CSS_USER_CARD, CSS_NAVIGATION,
            CSS_SIDEBAR_BADGES, CSS_FILTER_PANEL, CSS_ACTIONS,
        ]
        css = "\n".join(b.format_map(palette) for b in blocks)
        st.markdown(css, unsafe_allow_html=True)

    @classmethod
    def inject_block(cls, block_name: str) -> None:
        import streamlit as st

        css_block = cls._CSS_BLOCKS.get(block_name)
        if css_block is None:
            raise ValueError(
                f"Bloque '{block_name}' no existe. "
                f"Válidos: {list(cls._CSS_BLOCKS.keys())}"
            )
        st.markdown(css_block.format_map(cls._palette_dict()),
                    unsafe_allow_html=True)

    @classmethod
    def status_pill(cls, text: str, kind: str = "info") -> str:
        return helpers.status_pill(text, kind)

    @classmethod
    def section_header(cls, title: str, subtitle: str = "") -> str:
        return helpers.section_header(title, subtitle)

    @classmethod
    def info_banner(cls, text: str, kind: str = "info") -> str:
        return helpers.info_banner(text, kind)
