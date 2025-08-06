# -*- coding: utf-8 -*-
"""
صفحات المحتوى المختلفة
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, 
                             QListWidget, QProgressBar, QLabel, QFrame, QSpinBox,
                             QAbstractItemView)
from PyQt5.QtCore import Qt
from utils.config import DEFAULT_BACKUP_RETENTION


class BackupPage(QWidget):
    """صفحة النسخ الاحتياطي"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # عنوان الصفحة
        title = QLabel("النسخ الاحتياطي")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #2a82da; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # أزرار النسخ
        buttons_frame = QFrame()
        buttons_frame.setFrameStyle(QFrame.Box)
        buttons_frame.setStyleSheet("QFrame { border: 1px solid #4b749e; border-radius: 8px; padding: 15px; }")
        buttons_layout = QVBoxLayout(buttons_frame)
        
        self.backup_btn = QPushButton("ابدأ النسخ الاحتياطي")
        self.backup_btn.setStyleSheet("""
            QPushButton {
                font-size: 14px; 
                font-weight: bold; 
                background-color: #2a82da;
                padding: 15px;
                border-radius: 8px;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #3498db;
            }
        """)
        buttons_layout.addWidget(self.backup_btn)
        
        self.cancel_backup_btn = QPushButton("إلغاء النسخ")
        self.cancel_backup_btn.setEnabled(False)
        self.cancel_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        buttons_layout.addWidget(self.cancel_backup_btn)
        
        layout.addWidget(buttons_frame)
        
        # شريط التقدم
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.Box)
        progress_frame.setStyleSheet("QFrame { border: 1px solid #4b749e; border-radius: 8px; padding: 15px; }")
        progress_layout = QVBoxLayout(progress_frame)
        
        progress_title = QLabel("حالة العملية")
        progress_title.setStyleSheet("font-weight: bold; color: #f39c12; font-size: 12px;")
        progress_layout.addWidget(progress_title)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("جاهز للبدء")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #95a5a6; font-style: italic; margin-top: 5px;")
        progress_layout.addWidget(self.status_label)
        
        layout.addWidget(progress_frame)
        layout.addStretch()


class RestorePage(QWidget):
    """صفحة الاسترداد"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # عنوان الصفحة
        title = QLabel("الاسترداد")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #28a745; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # أزرار الاسترداد
        buttons_frame = QFrame()
        buttons_frame.setFrameStyle(QFrame.Box)
        buttons_frame.setStyleSheet("QFrame { border: 1px solid #4b749e; border-radius: 8px; padding: 15px; }")
        buttons_layout = QVBoxLayout(buttons_frame)
        
        self.restore_btn = QPushButton("استرداد النسخة المحددة")
        self.restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                padding: 15px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #34ce57;
            }
        """)
        buttons_layout.addWidget(self.restore_btn)
        
        self.cancel_restore_btn = QPushButton("إلغاء الاسترداد")
        self.cancel_restore_btn.setEnabled(False)
        self.cancel_restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                padding: 12px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        buttons_layout.addWidget(self.cancel_restore_btn)
        
        layout.addWidget(buttons_frame)
        
        # شريط التقدم للاسترداد
        progress_frame = QFrame()
        progress_frame.setFrameStyle(QFrame.Box)
        progress_frame.setStyleSheet("QFrame { border: 1px solid #4b749e; border-radius: 8px; padding: 15px; }")
        progress_layout = QVBoxLayout(progress_frame)
        
        progress_title = QLabel("حالة الاسترداد")
        progress_title.setStyleSheet("font-weight: bold; color: #f39c12; font-size: 12px;")
        progress_layout.addWidget(progress_title)
        
        self.restore_progress_bar = QProgressBar()
        self.restore_progress_bar.setRange(0, 100)
        progress_layout.addWidget(self.restore_progress_bar)
        
        self.restore_status_label = QLabel("جاهز للاسترداد")
        self.restore_status_label.setAlignment(Qt.AlignCenter)
        self.restore_status_label.setStyleSheet("color: #95a5a6; font-style: italic; margin-top: 5px;")
        progress_layout.addWidget(self.restore_status_label)
        
        layout.addWidget(progress_frame)
        layout.addStretch()


class FoldersPage(QWidget):
    """صفحة إدارة المجلدات"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.folder_widgets = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # عنوان الصفحة
        title = QLabel("إدارة المجلدات")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #3498db; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # منطقة المجلدات
        folders_frame = QFrame()
        folders_frame.setFrameStyle(QFrame.Box)
        folders_frame.setStyleSheet("QFrame { border: 1px solid #4b749e; border-radius: 8px; padding: 15px; }")
        folders_layout = QVBoxLayout(folders_frame)
        
        folders_label = QLabel("المجلدات المراد نسخها")
        folders_label.setStyleSheet("font-weight: bold; color: #3498db; font-size: 14px; margin-bottom: 10px;")
        folders_layout.addWidget(folders_label)
        
        # منطقة قابلة للتمرير للمجلدات
        from PyQt5.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #3c3f41;
                border: 1px solid #4b749e;
                border-radius: 6px;
            }
        """)
        
        self.folders_container = QWidget()
        self.folders_layout = QVBoxLayout(self.folders_container)
        self.folders_layout.setSpacing(5)
        self.folders_layout.addStretch()
        
        scroll_area.setWidget(self.folders_container)
        folders_layout.addWidget(scroll_area)
        
        # زر إضافة مجلد
        self.add_folder_btn = QPushButton("+ إضافة مجلد")
        self.add_folder_btn.setStyleSheet("""
            QPushButton {
                padding: 12px;
                font-weight: bold;
                background-color: #27ae60;
                border-radius: 6px;
                font-size: 12pt;
            }
            QPushButton:hover {
                background-color: #2ecc71;
            }
        """)
        folders_layout.addWidget(self.add_folder_btn)
        
        layout.addWidget(folders_frame)
        layout.addStretch()
    
    def add_folder_widget(self, folder_path, folder_name, is_enabled=True, is_default=False):
        """إضافة ويدجت مجلد جديد"""
        from PyQt5.QtWidgets import QCheckBox
        
        folder_widget = QWidget()
        folder_layout = QHBoxLayout(folder_widget)
        folder_layout.setContentsMargins(10, 5, 10, 5)
        
        # صندوق الاختيار
        checkbox = QCheckBox()
        checkbox.setChecked(is_enabled)
        checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 11pt;
                color: #d8d8d8;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #4b749e;
                background-color: #3c3f41;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #27ae60;
                background-color: #27ae60;
                border-radius: 3px;
            }
        """)
        
        # تسمية المجلد
        folder_label = QLabel(folder_name)
        if is_default:
            folder_label.setStyleSheet("color: #95a5a6; font-style: italic;")
        else:
            folder_label.setStyleSheet("color: #d8d8d8;")
        
        folder_layout.addWidget(checkbox)
        folder_layout.addWidget(folder_label)
        folder_layout.addStretch()
        
        # زر الحذف (فقط للمجلدات المخصصة)
        if not is_default:
            remove_btn = QPushButton("×")
            remove_btn.setFixedSize(25, 25)
            remove_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-weight: bold;
                    font-size: 14pt;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            remove_btn.clicked.connect(lambda: self.remove_folder_widget(folder_widget, folder_path))
            folder_layout.addWidget(remove_btn)
        
        # حفظ البيانات
        folder_widget.folder_path = folder_path
        folder_widget.checkbox = checkbox
        folder_widget.is_default = is_default
        
        # ربط تغيير الحالة بحفظ الإعدادات
        checkbox.stateChanged.connect(self.save_folder_settings)
        
        # إضافة إلى التخطيط
        self.folders_layout.insertWidget(self.folders_layout.count() - 1, folder_widget)
        self.folder_widgets.append(folder_widget)
        
        return folder_widget
    
    def remove_folder_widget(self, widget, folder_path):
        """إزالة ويدجت مجلد"""
        if widget in self.folder_widgets:
            self.folder_widgets.remove(widget)
            widget.setParent(None)
            widget.deleteLater()
            self.save_folder_settings()
    
    def save_folder_settings(self):
        """حفظ إعدادات المجلدات"""
        if self.parent_window and hasattr(self.parent_window, 'model'):
            folders_settings = []
            for widget in self.folder_widgets:
                folders_settings.append({
                    'path': str(widget.folder_path),
                    'enabled': widget.checkbox.isChecked(),
                    'is_default': widget.is_default
                })
            self.parent_window.model.save_folder_settings(folders_settings)
    
    def get_selected_folders(self):
        """الحصول على المجلدات المحددة"""
        selected = []
        for widget in self.folder_widgets:
            if widget.checkbox.isChecked():
                selected.append(widget.folder_path)
        return selected


class ExclusionsPage(QWidget):
    """صفحة الاستثناءات"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.exclusion_widgets = []
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # عنوان الصفحة
        title = QLabel("الاستثناءات")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # منطقة الاستثناءات
        exclusions_frame = QFrame()
        exclusions_frame.setFrameStyle(QFrame.Box)
        exclusions_frame.setStyleSheet("QFrame { border: 1px solid #4b749e; border-radius: 8px; padding: 15px; }")
        exclusions_layout = QVBoxLayout(exclusions_frame)
        
        exclusions_label = QLabel("أنماط الاستثناءات")
        exclusions_label.setStyleSheet("font-weight: bold; color: #e74c3c; font-size: 14px; margin-bottom: 10px;")
        exclusions_layout.addWidget(exclusions_label)
        
        # حقل إدخال الاستثناء الجديد
        from PyQt5.QtWidgets import QLineEdit
        input_layout = QHBoxLayout()
        
        self.exclusion_input = QLineEdit()
        self.exclusion_input.setPlaceholderText("أدخل نمط الاستثناء (مثال: *.log أو مجلد_مؤقت)")
        self.exclusion_input.setStyleSheet("""
            QLineEdit {
                background-color: #3c3f41;
                border: 2px solid #4b749e;
                border-radius: 6px;
                padding: 10px;
                font-size: 11pt;
                color: #d8d8d8;
            }
            QLineEdit:focus {
                border: 2px solid #e74c3c;
            }
        """)
        self.exclusion_input.returnPressed.connect(self.add_exclusion_from_input)
        
        add_btn = QPushButton("إضافة")
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                padding: 10px 15px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        add_btn.clicked.connect(self.add_exclusion_from_input)
        
        input_layout.addWidget(self.exclusion_input)
        input_layout.addWidget(add_btn)
        exclusions_layout.addLayout(input_layout)
        
        # منطقة قابلة للتمرير للاستثناءات
        from PyQt5.QtWidgets import QScrollArea
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea {
                background-color: #3c3f41;
                border: 1px solid #4b749e;
                border-radius: 6px;
            }
        """)
        
        self.exclusions_container = QWidget()
        self.exclusions_layout = QVBoxLayout(self.exclusions_container)
        self.exclusions_layout.setSpacing(5)
        self.exclusions_layout.addStretch()
        
        scroll_area.setWidget(self.exclusions_container)
        exclusions_layout.addWidget(scroll_area)
        
        layout.addWidget(exclusions_frame)
        layout.addStretch()
    
    def add_exclusion_from_input(self):
        """إضافة استثناء من حقل الإدخال"""
        exclusion_text = self.exclusion_input.text().strip()
        if exclusion_text:
            self.add_exclusion_widget(exclusion_text)
            self.exclusion_input.clear()
            self.save_exclusions()
    
    def add_exclusion_widget(self, exclusion_text):
        """إضافة ويدجت استثناء جديد"""
        # التحقق من عدم وجود الاستثناء مسبقاً
        for widget in self.exclusion_widgets:
            if widget.exclusion_text == exclusion_text:
                return
        
        exclusion_widget = QWidget()
        exclusion_layout = QHBoxLayout(exclusion_widget)
        exclusion_layout.setContentsMargins(10, 5, 10, 5)
        
        # تسمية الاستثناء
        exclusion_label = QLabel(exclusion_text)
        exclusion_label.setStyleSheet("""
            QLabel {
                color: #d8d8d8;
                font-size: 11pt;
                padding: 5px;
                background-color: #2c2f31;
                border-radius: 4px;
            }
        """)
        
        exclusion_layout.addWidget(exclusion_label)
        exclusion_layout.addStretch()
        
        # زر الحذف
        remove_btn = QPushButton("×")
        remove_btn.setFixedSize(25, 25)
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 12px;
                font-weight: bold;
                font-size: 14pt;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_btn.clicked.connect(lambda: self.remove_exclusion_widget(exclusion_widget))
        exclusion_layout.addWidget(remove_btn)
        
        # حفظ البيانات
        exclusion_widget.exclusion_text = exclusion_text
        
        # إضافة إلى التخطيط
        self.exclusions_layout.insertWidget(self.exclusions_layout.count() - 1, exclusion_widget)
        self.exclusion_widgets.append(exclusion_widget)
        
        return exclusion_widget
    
    def remove_exclusion_widget(self, widget):
        """إزالة ويدجت استثناء"""
        if widget in self.exclusion_widgets:
            self.exclusion_widgets.remove(widget)
            widget.setParent(None)
            widget.deleteLater()
            self.save_exclusions()
    
    def save_exclusions(self):
        """حفظ الاستثناءات"""
        if self.parent_window and hasattr(self.parent_window, 'model'):
            exclusions = [widget.exclusion_text for widget in self.exclusion_widgets]
            self.parent_window.model.save_exclusions(exclusions)
    
    def get_exclusions(self):
        """الحصول على قائمة الاستثناءات"""
        return [widget.exclusion_text for widget in self.exclusion_widgets]
    
    def clear_exclusions(self):
        """مسح جميع الاستثناءات"""
        for widget in self.exclusion_widgets[:]:
            self.remove_exclusion_widget(widget)
    
    def load_exclusions(self, exclusions):
        """تحميل الاستثناءات"""
        self.clear_exclusions()
        for exclusion in exclusions:
            self.add_exclusion_widget(exclusion)


class BackupsPage(QWidget):
    """صفحة النسخ المتاحة"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # عنوان الصفحة
        title = QLabel("النسخ الاحتياطية المتاحة")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #9b59b6; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # قائمة النسخ
        backups_frame = QFrame()
        backups_frame.setFrameStyle(QFrame.Box)
        backups_frame.setStyleSheet("QFrame { border: 1px solid #4b749e; border-radius: 8px; padding: 15px; }")
        backups_layout = QVBoxLayout(backups_frame)
        
        backups_label = QLabel("النسخ المحفوظة")
        backups_label.setStyleSheet("font-weight: bold; color: #9b59b6; font-size: 14px; margin-bottom: 10px;")
        backups_layout.addWidget(backups_label)
        
        self.backups_list = QListWidget()
        self.backups_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.backups_list.setStyleSheet("""
            QListWidget {
                background-color: #3c3f41;
                border: 1px solid #4b749e;
                border-radius: 6px;
                padding: 8px;
                font-size: 11pt;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid #555;
                border-radius: 4px;
                margin: 2px;
            }
            QListWidget::item:selected {
                background-color: #9b59b6;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #8e44ad;
            }
        """)
        backups_layout.addWidget(self.backups_list)
        
        # أزرار إدارة النسخ
        backup_management_layout = QHBoxLayout()
        
        self.delete_backup_btn = QPushButton("حذف المحدد")
        self.delete_backup_btn.setStyleSheet("padding: 10px; font-weight: bold; background-color: #dc3545;")
        
        self.refresh_btn = QPushButton("تحديث القائمة")
        self.refresh_btn.setStyleSheet("padding: 10px; font-weight: bold;")
        
        backup_management_layout.addWidget(self.delete_backup_btn)
        backup_management_layout.addWidget(self.refresh_btn)
        backups_layout.addLayout(backup_management_layout)
        
        layout.addWidget(backups_frame)
        layout.addStretch()


class SettingsPage(QWidget):
    """صفحة الإعدادات"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.setup_ui()
    
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # عنوان الصفحة
        title = QLabel("إعدادات النسخ")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: #f39c12; margin-bottom: 15px;")
        layout.addWidget(title)
        
        # إعدادات الاحتفاظ
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.Box)
        settings_frame.setStyleSheet("QFrame { border: 1px solid #4b749e; border-radius: 8px; padding: 20px; }")
        settings_layout = QVBoxLayout(settings_frame)
        
        retention_label = QLabel("إعدادات الاحتفاظ بالنسخ")
        retention_label.setStyleSheet("font-weight: bold; color: #f39c12; font-size: 14px; margin-bottom: 15px;")
        settings_layout.addWidget(retention_label)
        
        retention_layout = QHBoxLayout()
        retention_layout.addWidget(QLabel("الاحتفاظ بآخر"))
        
        self.retention_spinbox = QSpinBox()
        self.retention_spinbox.setMinimum(1)
        self.retention_spinbox.setMaximum(50)
        self.retention_spinbox.setValue(DEFAULT_BACKUP_RETENTION)
        self.retention_spinbox.setStyleSheet("""
            QSpinBox {
                background-color: #3c3f41;
                border: 1px solid #4b749e;
                padding: 8px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12pt;
                min-width: 80px;
            }
            QSpinBox:focus {
                border: 2px solid #37588a;
            }
        """)
        retention_layout.addWidget(self.retention_spinbox)
        retention_layout.addWidget(QLabel("نسخة"))
        retention_layout.addStretch()
    
        settings_layout.addLayout(retention_layout)
        
        # معلومات إضافية
        info_label = QLabel("سيتم حذف النسخ الأقدم تلقائياً عند تجاوز العدد المحدد")
        info_label.setStyleSheet("color: #95a5a6; font-style: italic; margin-top: 10px;")
        settings_layout.addWidget(info_label)
        
        # خيار تجاهل الملفات المخفية
        from PyQt5.QtWidgets import QCheckBox
        hidden_files_layout = QHBoxLayout()
        
        self.ignore_hidden_checkbox = QCheckBox("تجاهل الملفات والمجلدات المخفية (التي تبدأ بنقطة)")
        self.ignore_hidden_checkbox.setChecked(True)
        self.ignore_hidden_checkbox.setStyleSheet("""
            QCheckBox {
                font-size: 11pt;
                color: #d8d8d8;
                margin-top: 15px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #4b749e;
                background-color: #3c3f41;
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #f39c12;
                background-color: #f39c12;
                border-radius: 3px;
            }
        """)
        
        hidden_files_layout.addWidget(self.ignore_hidden_checkbox)
        hidden_files_layout.addStretch()
        settings_layout.addLayout(hidden_files_layout)
        
        layout.addWidget(settings_frame)
        layout.addStretch()