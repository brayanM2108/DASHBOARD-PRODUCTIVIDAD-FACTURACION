from .palette import (
    NAVY, NAVY2, BLUE, BLUE_LIGHT,
    ORANGE, ORANGE_LIGHT,
    SUCCESS, SUCCESS_LIGHT,
    DANGER, DANGER_LIGHT,
    WARNING, WARNING_LIGHT,
    MUTED,
)


def status_pill(text: str, kind: str = "info") -> str:
    colors = {
        "info":    (BLUE_LIGHT,    BLUE),
        "success": (SUCCESS_LIGHT, SUCCESS),
        "warning": (WARNING_LIGHT, WARNING),
        "danger":  (DANGER_LIGHT,  DANGER),
        "orange":  (ORANGE_LIGHT,  ORANGE),
        "muted":   ("#F1F5F9",     MUTED),
    }
    bg, fg = colors.get(kind, colors["info"])
    return (
        f"<span style='display:inline-flex;align-items:center;"
        f"padding:2px 10px;border-radius:20px;font-size:11px;"
        f"font-weight:500;background:{bg};color:{fg};'>{text}</span>"
    )


def section_header(title: str, subtitle: str = "") -> str:
    sub_html = (
        f"<div style='font-size:11px;color:{MUTED};margin-top:2px'>"
        f"{subtitle}</div>"
        if subtitle else ""
    )
    return (
        f"<div style='border-left:3px solid {ORANGE};"
        f"padding-left:10px;margin-bottom:12px'>"
        f"<div style='font-size:14px;font-weight:600;color:{NAVY}'>"
        f"{title}</div>"
        f"{sub_html}"
        f"</div>"
    )


def info_banner(text: str, kind: str = "info") -> str:
    icons = {
        "info":    ("ℹ️", BLUE_LIGHT,    "#B3C8EF", NAVY2),
        "success": ("✅", SUCCESS_LIGHT, "#C6F6D5", SUCCESS),
        "warning": ("⚠️", WARNING_LIGHT, "#FAF089", WARNING),
        "danger":  ("❌", DANGER_LIGHT,  "#FEB2B2", DANGER),
    }
    icon, bg, border, fg = icons.get(kind, icons["info"])
    return (
        f"<div style='display:flex;align-items:flex-start;gap:10px;"
        f"padding:11px 14px;border-radius:8px;background:{bg};"
        f"border:0.5px solid {border};font-size:12px;color:{fg};"
        f"margin-bottom:8px'>"
        f"<span style='flex-shrink:0;margin-top:1px'>{icon}</span>"
        f"<span>{text}</span></div>"
    )
