"""style.py -- design tokens, dark trading-desk theme."""

COLORS = {
    "bg_app": "#0B0E14", "bg_panel": "#151922", "bg_card": "#1C212D",
    "border": "#262C3A", "text_primary": "#E8E6E0", "text_secondary": "#8A90A0",
    "text_muted": "#5A5F6E", "amber": "#FFB000", "teal": "#00D9C0", "red": "#FF5C5C",
}

CONTAINER_STYLE = {
    "backgroundColor": COLORS["bg_app"], "color": COLORS["text_primary"],
    "fontFamily": "'Inter', sans-serif", "padding": "24px",
    "minHeight": "100vh", "boxSizing": "border-box",
}

PANEL_STYLE = {
    "backgroundColor": COLORS["bg_panel"], "border": f"1px solid {COLORS['border']}",
    "borderRadius": "4px", "padding": "18px", "marginBottom": "16px",
}

CARD_STYLE = {
    "backgroundColor": COLORS["bg_card"], "border": f"1px solid {COLORS['border']}",
    "borderRadius": "4px", "padding": "12px 14px",
}

LABEL_STYLE = {
    "color": COLORS["text_secondary"], "fontSize": "11px", "fontWeight": "600",
    "textTransform": "uppercase", "letterSpacing": "0.5px", "marginBottom": "4px",
    "fontFamily": "'JetBrains Mono', monospace",
}

VALUE_STYLE = {
    "color": COLORS["text_primary"], "fontSize": "22px", "fontWeight": "700",
    "fontFamily": "'JetBrains Mono', monospace",
}

PANEL_TITLE_STYLE = {
    "color": COLORS["text_primary"], "fontSize": "13px", "fontWeight": "700",
    "textTransform": "uppercase", "letterSpacing": "1px",
    "borderBottom": f"1px solid {COLORS['border']}", "paddingBottom": "8px",
    "marginBottom": "14px", "fontFamily": "'JetBrains Mono', monospace",
}
