# -*- coding: utf-8 -*-
"""
مكون الشريط الجانبي
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QButtonGroup
from PyQt5.QtCore import Qt


class Sidebar(QWidget):
    """الشريط الجانبي للتنقل بين الصفحات"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.sidebar_buttons = {}
        self.sidebar_button_group = None
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة الشريط الجانبي"""
        self.setObjectName("sidebar")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(10)
        
        # عنوان الشريط الجانبي
        title_label = QLabel("الوظائف")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #e67e22; margin-bottom: 15px; text-align: center;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # مجموعة أزرار الشريط الجانبي
        self.sidebar_button_group = QButtonGroup()
        self.sidebar_button_group.setExclusive(True)
        
        # أزرار الوظائف
        buttons_data = [
            ("backup", "النسخ الاحتياطي", "🔄"),
            ("restore", "الاسترداد", "📥"),
            ("folders", "إدارة المجلدات", "📁"),
            ("exclusions", "الاستثناءات", "🚫"),
            ("backups", "النسخ المتاحة", "💾"),
            ("settings", "الإعدادات", "⚙️")
        ]
        
        for page_id, text, icon in buttons_data:
            btn = QPushButton(f"{icon}\n{text}")
            btn.setObjectName("sidebar_button")
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, p=page_id: self.switch_page(p))
            
            self.sidebar_buttons[page_id] = btn
            self.sidebar_button_group.addButton(btn)
            layout.addWidget(btn)
        
        # تحديد الصفحة الافتراضية
        self.sidebar_buttons["backup"].setChecked(True)
        
        layout.addStretch()
    
    def switch_page(self, page_id):
        """تبديل الصفحة المعروضة"""
        if self.parent_window:
            self.parent_window.switch_page(page_id)