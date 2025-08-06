# -*- coding: utf-8 -*-
"""
النافذة الرئيسية المبسطة - تطبيق MVP Pattern مع Composition
"""

import sys
from pathlib import Path
from datetime import datetime
from typing import List, Optional

from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QListWidgetItem, QFileDialog, QMessageBox, QFrame,
                             QInputDialog, QStackedWidget)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor

from utils.config import (TOOL_NAME, BACKUP_DIR, HOME_DIR, DEFAULT_FOLDERS)
from interfaces.ui_interfaces import IMainView
from ui.backup_model import BackupModel
from ui.main_presenter import MainPresenter
from ui.components.theme import DARK_THEME_STYLESHEET
from ui.components.sidebar import Sidebar
from ui.components.pages import (BackupPage, RestorePage, FoldersPage, 
                                ExclusionsPage, BackupsPage, SettingsPage)


class AlHirzApp(QMainWindow):
    """الواجهة الرئيسية المبسطة"""
    
    def __init__(self):
        super().__init__()
        
        # إعداد MVP Pattern
        self.model = BackupModel()
        self.presenter = MainPresenter(self, self.model)
        
        # متغيرات الواجهة
        self.content_stack = None
        self.current_page = "backup"
        self.pages = {}
        
        self.setup_environment()
        self.setup_ui()
        self.connect_signals()
        self.load_initial_data()

    def setup_ui(self):
        """إعداد الواجهة الرئيسية"""
        self.setWindowTitle(TOOL_NAME + " - الحصن الرقمي الأمين")
        self.resize(1200, 700)
        self.setMinimumSize(1000, 600)
        self.setStyleSheet(DARK_THEME_STYLESHEET)

        # إنشاء تخطيط أفقي رئيسي
        main_widget = QWidget()
        main_layout = QHBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # الشريط الجانبي
        self.sidebar = Sidebar(self)
        main_layout.addWidget(self.sidebar)
        
        # فاصل عمودي
        separator = QFrame()
        separator.setFrameShape(QFrame.VLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("color: #4b749e; max-width: 2px;")
        main_layout.addWidget(separator)
        
        # منطقة المحتوى الرئيسية
        self.create_content_area(main_layout)

        self.setCentralWidget(main_widget)

    def create_content_area(self, main_layout):
        """إنشاء منطقة المحتوى الرئيسية"""
        content_widget = QWidget()
        content_widget.setObjectName("content_area")
        content_layout = QVBoxLayout(content_widget)
        content_layout.setContentsMargins(20, 20, 20, 20)
        content_layout.setSpacing(15)
        
        # إنشاء مكدس الصفحات
        self.content_stack = QStackedWidget()
        
        # إنشاء صفحات المحتوى
        self.create_pages()
        
        content_layout.addWidget(self.content_stack)
        main_layout.addWidget(content_widget, 1)

    def create_pages(self):
        """إنشاء جميع الصفحات"""
        # صفحة النسخ الاحتياطي
        self.backup_page = BackupPage(self)
        self.pages['backup'] = self.backup_page
        self.content_stack.addWidget(self.backup_page)
        
        # صفحة الاسترداد
        self.restore_page = RestorePage(self)
        self.pages['restore'] = self.restore_page
        self.content_stack.addWidget(self.restore_page)
        
        # صفحة المجلدات
        self.folders_page = FoldersPage(self)
        self.pages['folders'] = self.folders_page
        self.content_stack.addWidget(self.folders_page)
        
        # صفحة الاستثناءات
        self.exclusions_page = ExclusionsPage(self)
        self.pages['exclusions'] = self.exclusions_page
        self.content_stack.addWidget(self.exclusions_page)
        
        # صفحة النسخ المتاحة
        self.backups_page = BackupsPage(self)
        self.pages['backups'] = self.backups_page
        self.content_stack.addWidget(self.backups_page)
        
        # صفحة الإعدادات
        self.settings_page = SettingsPage(self)
        self.pages['settings'] = self.settings_page
        self.content_stack.addWidget(self.settings_page)

    def connect_signals(self):
        """ربط الإشارات بالدوال"""
        # أزرار النسخ الاحتياطي
        self.backup_page.backup_btn.clicked.connect(self.presenter.start_backup)
        self.backup_page.cancel_backup_btn.clicked.connect(self.presenter.cancel_operation)
        
        # أزرار الاسترداد
        self.restore_page.restore_btn.clicked.connect(self.presenter.start_restore)
        self.restore_page.cancel_restore_btn.clicked.connect(self.presenter.cancel_operation)
        
        # أزرار المجلدات
        self.folders_page.add_folder_btn.clicked.connect(self.add_custom_folder)
        
        # أزرار النسخ المتاحة
        self.backups_page.delete_backup_btn.clicked.connect(self.presenter.delete_backups)
        self.backups_page.refresh_btn.clicked.connect(self.presenter.refresh_backups)

    def switch_page(self, page_id):
        """تبديل الصفحة المعروضة"""
        page_indices = {
            "backup": 0,
            "restore": 1,
            "folders": 2,
            "exclusions": 3,
            "backups": 4,
            "settings": 5
        }
        
        if page_id in page_indices:
            self.content_stack.setCurrentIndex(page_indices[page_id])
            self.current_page = page_id

    def setup_environment(self):
        """إعداد البيئة"""
        try:
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            QMessageBox.critical(self, "خطأ في الإعداد", f"تعذّر إنشاء مجلدات الإعدادات:\n{e}")
            sys.exit(1)

    def load_initial_data(self):
        """تحميل البيانات الأولية"""
        self.load_folder_settings()
        self.load_exclusions()
        self.load_settings()
        self.refresh_backups_list()

    # === تنفيذ IMainView ===
    
    def get_selected_folders(self) -> List[Path]:
        """الحصول على المجلدات المحددة"""
        return self.folders_page.get_selected_folders()
    
    def get_exclusions(self) -> List[str]:
        """الحصول على قائمة الاستثناءات"""
        return self.exclusions_page.get_exclusions()
    
    def get_selected_backup(self) -> Optional[Path]:
        """الحصول على النسخة المحددة للاسترداد"""
        selected_items = self.backups_page.backups_list.selectedItems()
        if len(selected_items) == 1:
            return selected_items[0].data(Qt.UserRole)
        return None
    
    def get_selected_backups_for_deletion(self) -> List[Path]:
        """الحصول على النسخ المحددة للحذف"""
        selected_items = self.backups_page.backups_list.selectedItems()
        return [item.data(Qt.UserRole) for item in selected_items if item.data(Qt.UserRole) is not None]
    
    def get_retention_count(self) -> int:
        """الحصول على عدد النسخ المراد الاحتفاظ بها"""
        return self.settings_page.retention_spinbox.value()
    
    def show_message(self, title: str, message: str, message_type: str = "info") -> None:
        """عرض رسالة للمستخدم"""
        if message_type == "info":
            QMessageBox.information(self, title, message)
        elif message_type == "warning":
            QMessageBox.warning(self, title, message)
        elif message_type == "error":
            QMessageBox.critical(self, title, message)
    
    def show_confirmation(self, title: str, message: str) -> bool:
        """عرض رسالة تأكيد"""
        reply = QMessageBox.question(self, title, message, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        return reply == QMessageBox.Yes
    
    def update_progress(self, value: int, status: str, operation_type: str) -> None:
        """تحديث شريط التقدم"""
        if operation_type == 'backup':
            self.backup_page.progress_bar.setValue(value)
            self.backup_page.status_label.setText(status)
        elif operation_type == 'restore':
            self.restore_page.restore_progress_bar.setValue(value)
            self.restore_page.restore_status_label.setText(status)
    
    def toggle_controls(self, enable: bool, operation_type: str) -> None:
        """تفعيل/تعطيل عناصر التحكم"""
        if operation_type == 'backup':
            self.backup_page.backup_btn.setEnabled(enable)
            self.backup_page.cancel_backup_btn.setEnabled(not enable)
            self.folders_page.add_folder_btn.setEnabled(enable)
            self.restore_page.restore_btn.setEnabled(enable)
            self.backups_page.delete_backup_btn.setEnabled(enable)
            self.exclusions_page.exclusion_input.setEnabled(enable)
            self.backups_page.backups_list.setEnabled(enable)
        else:  # restore
            self.restore_page.restore_btn.setEnabled(enable)
            self.restore_page.cancel_restore_btn.setEnabled(not enable)
            self.backups_page.delete_backup_btn.setEnabled(enable)
            self.backups_page.backups_list.setEnabled(enable)
            self.backup_page.backup_btn.setEnabled(enable)
    
    def refresh_backups_list(self) -> None:
        """تحديث قائمة النسخ الاحتياطية"""
        self.populate_backups_list()

    # === دوال مساعدة ===
    
    def load_exclusions(self):
        """تحميل الاستثناءات من Model"""
        exclusions = self.model.get_exclusions()
        self.exclusions_page.load_exclusions(exclusions)
    
    def load_folder_settings(self):
        """تحميل إعدادات المجلدات"""
        # تحميل المجلدات المحفوظة
        saved_folders = self.model.get_folder_settings()
        
        # إضافة المجلدات الافتراضية أولاً
        for folder_name in DEFAULT_FOLDERS:
            path = HOME_DIR / folder_name
            if path.is_dir():
                # البحث عن الإعداد المحفوظ
                saved_setting = next((f for f in saved_folders if f['path'] == str(path) and f.get('is_default', False)), None)
                is_enabled = saved_setting['enabled'] if saved_setting else True
                
                self.folders_page.add_folder_widget(
                    folder_path=path,
                    folder_name=f"{folder_name} (افتراضي)",
                    is_enabled=is_enabled,
                    is_default=True
                )
        
        # إضافة المجلدات المخصصة
        for folder_setting in saved_folders:
            if not folder_setting.get('is_default', False):
                path = Path(folder_setting['path'])
                if path.exists() and path.is_dir():
                    self.folders_page.add_folder_widget(
                        folder_path=path,
                        folder_name=str(path),
                        is_enabled=folder_setting['enabled'],
                        is_default=False
                    )
    
    def load_settings(self):
        """تحميل الإعدادات العامة"""
        # تحميل إعداد تجاهل الملفات المخفية
        ignore_hidden = self.model.get_ignore_hidden_files()
        self.settings_page.ignore_hidden_checkbox.setChecked(ignore_hidden)
        
        # ربط تغيير الإعداد بحفظه
        self.settings_page.ignore_hidden_checkbox.stateChanged.connect(self.save_ignore_hidden_setting)
    
    def save_ignore_hidden_setting(self):
        """حفظ إعداد تجاهل الملفات المخفية"""
        ignore_hidden = self.settings_page.ignore_hidden_checkbox.isChecked()
        self.model.set_ignore_hidden_files(ignore_hidden)

    def add_custom_folder(self):
        """إضافة مجلد مخصص"""
        folder_path = QFileDialog.getExistingDirectory(self, "اختر مجلداً", str(HOME_DIR))
        if folder_path:
            path_obj = Path(folder_path)
            
            # التحقق من عدم وجود المجلد مسبقاً
            for widget in self.folders_page.folder_widgets:
                if widget.folder_path == path_obj:
                    QMessageBox.warning(self, "مجلد مكرر", "هذا المجلد موجود بالفعل.")
                    return
            
            # إضافة المجلد الجديد
            self.folders_page.add_folder_widget(
                folder_path=path_obj,
                folder_name=str(path_obj),
                is_enabled=True,
                is_default=False
            )

    def populate_backups_list(self):
        """تحديث قائمة النسخ الاحتياطية"""
        self.backups_page.backups_list.clear()
        available_backups = self.model.get_available_backups()

        if not available_backups:
            item = QListWidgetItem("لا توجد نسخ احتياطية متاحة.")
            item.setFlags(item.flags() & ~Qt.ItemIsSelectable)
            self.backups_page.backups_list.addItem(item)
            return

        for backup_file in available_backups:
            file_date = datetime.fromtimestamp(backup_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
            size_mb = backup_file.stat().st_size / (1024*1024)
            item = QListWidgetItem(f"{backup_file.name}  ({file_date}) - {size_mb:.2f} MB")
            item.setData(Qt.UserRole, backup_file)
            self.backups_page.backups_list.addItem(item)

    def closeEvent(self, event):
        """معالجة إغلاق التطبيق"""
        if hasattr(self.presenter, 'current_worker') and self.presenter.current_worker and self.presenter.current_worker.isRunning():
            reply = QMessageBox.question(self, 'عملية نشطة', "توجد عملية قيد التشغيل. هل تريد الخروج؟", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                self.presenter.cancel_operation()
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()