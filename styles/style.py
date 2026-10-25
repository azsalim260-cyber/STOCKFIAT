"""
styles/style.py — Global QSS stylesheet (corporate blue/grey theme)
"""

STYLE = """
/* ── Global ── */
QMainWindow, QDialog {
    background-color: #F4F6F9;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    font-size: 13px;
    color: #2C3E50;
}

/* ── Toolbar ── */
QToolBar {
    background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                stop:0 #1A3A5C, stop:1 #2E86C1);
    border: none;
    padding: 4px 8px;
    spacing: 6px;
}
QToolBar QLabel {
    color: white;
    font-size: 16px;
    font-weight: bold;
    padding: 0 12px;
}
QToolBar QPushButton {
    background-color: rgba(255,255,255,0.15);
    color: white;
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: 600;
    min-width: 90px;
}
QToolBar QPushButton:hover   { background-color: rgba(255,255,255,0.28); border: 1px solid white; }
QToolBar QPushButton:pressed { background-color: rgba(255,255,255,0.10); }

/* ── Action buttons ── */
QPushButton#btn_add    { background-color: #27AE60; color: white; border: none;
                          border-radius: 6px; padding: 6px 16px; font-weight: 700; }
QPushButton#btn_add:hover    { background-color: #229954; }
QPushButton#btn_edit   { background-color: #2980B9; color: white; border: none;
                          border-radius: 6px; padding: 6px 16px; font-weight: 700; }
QPushButton#btn_edit:hover   { background-color: #1F618D; }
QPushButton#btn_del    { background-color: #C0392B; color: white; border: none;
                          border-radius: 6px; padding: 6px 16px; font-weight: 700; }
QPushButton#btn_del:hover    { background-color: #A93226; }
QPushButton#btn_export { background-color: #8E44AD; color: white; border: none;
                          border-radius: 6px; padding: 6px 16px; font-weight: 700; }
QPushButton#btn_export:hover { background-color: #7D3C98; }

/* ── Pagination buttons ── */
QPushButton#btn_prev, QPushButton#btn_next {
    background-color: #2E86C1; color: white; border: none;
    border-radius: 5px; padding: 4px 14px; font-weight: 600;
}
QPushButton#btn_prev:hover, QPushButton#btn_next:hover { background-color: #1A5276; }
QPushButton#btn_prev:disabled, QPushButton#btn_next:disabled {
    background-color: #BDC3C7; color: #7F8C8D;
}

/* ── Search bar ── */
QLineEdit#search_bar {
    border: 2px solid #BDC3C7;
    border-radius: 18px;
    padding: 6px 14px;
    background-color: white;
    min-width: 260px;
}
QLineEdit#search_bar:focus { border-color: #2E86C1; }

/* ── Table ── */
QTableWidget {
    background-color: white;
    alternate-background-color: #EBF5FB;
    border: 1px solid #D5D8DC;
    border-radius: 6px;
    gridline-color: #D5D8DC;
    selection-background-color: #2E86C1;
    selection-color: white;
}
QTableWidget::item { padding: 6px 8px; }
QHeaderView::section {
    background: qlineargradient(x1:0,y1:0,x2:0,y2:1,
                stop:0 #2E86C1, stop:1 #1A5276);
    color: white; font-weight: 700; padding: 8px 6px;
    border: none; border-right: 1px solid #1A5276; font-size: 12px;
}
QHeaderView::section:first { border-radius: 6px 0 0 0; }
QHeaderView::section:last  { border-radius: 0 6px 0 0; border-right: none; }

/* ── Status bar ── */
QStatusBar {
    background-color: #1A3A5C; color: #AED6F1;
    font-size: 12px; padding: 2px 10px;
}

/* ── Progress bar (shown during loading) ── */
QProgressBar {
    border: 1px solid #BDC3C7; border-radius: 4px;
    text-align: center; background: white;
}
QProgressBar::chunk { background-color: #2E86C1; border-radius: 4px; }

/* ── Dialog ── */
QDialog QLabel     { font-weight: 600; color: #1A5276; }
QDialog QLineEdit  {
    border: 1.5px solid #BDC3C7; border-radius: 5px;
    padding: 7px 10px; background: white; min-width: 260px;
}
QDialog QLineEdit:focus { border-color: #2E86C1; }
QGroupBox {
    font-weight: 700; color: #1A5276;
    border: 2px solid #AED6F1; border-radius: 8px;
    margin-top: 12px; padding: 8px;
}
QGroupBox::title {
    subcontrol-origin: margin; subcontrol-position: top left;
    padding: 0 6px; background-color: #F4F6F9;
}
QPushButton#btn_save {
    background-color: #27AE60; color: white; border: none;
    border-radius: 6px; padding: 8px 28px; font-weight: 700; font-size: 14px;
}
QPushButton#btn_save:hover   { background-color: #229954; }
QPushButton#btn_cancel {
    background-color: #95A5A6; color: white; border: none;
    border-radius: 6px; padding: 8px 28px; font-weight: 700; font-size: 14px;
}
QPushButton#btn_cancel:hover { background-color: #7F8C8D; }

/* ── ComboBox ── */
QComboBox {
    border: 2px solid #BDC3C7; border-radius: 14px;
    padding: 5px 10px; background: white; min-width: 140px;
}
QComboBox:focus { border-color: #2E86C1; }
QComboBox QAbstractItemView {
    background: white; border: 1px solid #BDC3C7;
    selection-background-color: #2E86C1; selection-color: white;
}
"""

