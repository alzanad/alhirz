# -*- coding: utf-8 -*-
"""
ثيم التطبيق والأنماط المرئية
"""

DARK_THEME_STYLESHEET = """
    QWidget {
        background-color: #2b2b2b;
        color: #d8d8d8;
        font-family: 'Segoe UI', Arial, sans-serif;
        font-size: 10pt;
    }
    QMainWindow {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #2b2b2b, stop: 1 #1e1e1e);
        border: 2px solid #37588a;
        border-radius: 8px;
    }
    QPushButton {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #37588a, stop: 1 #2c4a73);
        color: white;
        padding: 10px 15px;
        border-radius: 6px;
        border: 1px solid #4b749e;
        font-weight: bold;
        min-height: 20px;
    }
    QPushButton:hover {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #4b749e, stop: 1 #37588a);
        border: 1px solid #5a8bc4;
    }
    QPushButton:pressed {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #e67e22, stop: 1 #d35400);
        border: 1px solid #f39c12;
    }
    QPushButton:disabled {
        background-color: #555;
        color: #888;
        border: 1px solid #666;
    }
    QPushButton[objectName="sidebar_button"] {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #3c3f41, stop: 1 #2c2f31);
        border: 1px solid #4b749e;
        border-radius: 8px;
        padding: 15px 10px;
        margin: 2px;
        text-align: center;
        font-size: 11pt;
        font-weight: bold;
    }
    QPushButton[objectName="sidebar_button"]:hover {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #4b749e, stop: 1 #37588a);
        border: 1px solid #5a8bc4;
    }
    QPushButton[objectName="sidebar_button"]:checked {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #e67e22, stop: 1 #d35400);
        border: 1px solid #f39c12;
        color: white;
    }
    QListWidget {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #3c3f41, stop: 1 #2c2f31);
        border: 2px solid #4b749e;
        border-radius: 6px;
        padding: 5px;
        selection-background-color: #37588a;
    }
    QListWidget::item {
        padding: 8px;
        border-bottom: 1px solid #555;
        border-radius: 4px;
        margin: 2px;
    }
    QListWidget::item:selected {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #37588a, stop: 1 #2c4a73);
        color: white;
        border: 1px solid #4b749e;
    }
    QListWidget::item:hover {
        background-color: #4a4a4a;
    }
    QProgressBar {
        border: 2px solid #4b749e;
        border-radius: 6px;
        text-align: center;
        color: white;
        font-weight: bold;
        background-color: #3c3f41;
        min-height: 20px;
    }
    QProgressBar::chunk {
        background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                                    stop: 0 #e67e22, stop: 1 #f39c12);
        border-radius: 4px;
        margin: 1px;
    }
    QLabel {
        background-color: transparent;
        color: #d8d8d8;
    }
    QSpinBox {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #3c3f41, stop: 1 #2c2f31);
        border: 2px solid #4b749e;
        padding: 8px;
        border-radius: 4px;
        font-weight: bold;
        color: white;
        min-width: 60px;
    }
    QSpinBox:focus {
        border: 2px solid #37588a;
    }
    QFrame {
        background-color: transparent;
    }
    QFrame[frameShape="4"] { /* VLine */
        color: #4b749e;
        background-color: #4b749e;
        max-width: 2px;
    }
    QFrame[frameShape="5"] { /* HLine */
        color: #4b749e;
        background-color: #4b749e;
        max-height: 2px;
    }
    QWidget[objectName="sidebar"] {
        background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                                    stop: 0 #3c3f41, stop: 1 #2c2f31);
        border-left: 2px solid #4b749e;
        min-width: 200px;
        max-width: 200px;
    }
    QWidget[objectName="content_area"] {
        background-color: #2b2b2b;
        border: none;
    }
"""