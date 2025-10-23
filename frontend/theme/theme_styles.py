# ============================
# alumprocncn - Fusion-like Styles
# ============================

def fusion_palette(theme: str):
    dark = (theme == "dark")
    colors = {
        "bg": "#202124" if dark else "#F1F3F4",
        "fg": "#E8EAED" if dark else "#202124",
        "hover": "#3C4043" if dark else "#E0E3E7",
        "sep": "#2A2B2E" if dark else "#DADCE0",
        "viewer_bg": "#1E1F22" if dark else "#FFFFFF",
    }
    return colors

def fusion_stylesheet(theme: str) -> str:
    c = fusion_palette(theme)
    return f"""
    /* نافذة البرنامج */
    QMainWindow#AlumProMainWindow {{
        background-color: {c['bg']};
        color: {c['fg']};
    }}

    /* النصوص */
    QLabel {{
        color: {c['fg']};
        font-size: 15px;
    }}

    /* أزرار التولبار/أزرار عادية */
    QToolBar {{
        background: {c['bg']};
        spacing: 6px;
        border: none;
    }}
    QToolBar QToolButton {{
        background: transparent;
        color: {c['fg']};
        border: none;
        padding: 6px 10px;
        border-radius: 6px;
    }}
    QToolBar QToolButton:hover {{
        background: {c['hover']};
    }}

    /* فواصل رفيعة مثل Fusion */
    QFrame#TopSeparator {{
        background-color: {c['sep']};
        min-height: 1px;
        max-height: 1px;
    }}

    /* منطقة العارض (غلاف فقط) إن وجدت */
    QWidget#ViewerContainer {{
        background: {c['viewer_bg']};
        border-radius: 10px;
    }}

    /* Dock panels */
    QDockWidget {{
        titlebar-close-icon: url(none);
        titlebar-normal-icon: url(none);
        background: {c['bg']};
        color: {c['fg']};
        border: 1px solid {c['sep']};
    }}
    QDockWidget::title {{
        background: {c['bg']};
        color: {c['fg']};
        padding: 6px 8px;
    }}

    /* أزرار عامة */
    QPushButton {{
        background: transparent;
        color: {c['fg']};
        border: none;
        border-radius: 6px;
        padding: 6px 12px;
    }}
    QPushButton:hover {{
        background: {c['hover']};
    }}
    """
