# -*- coding: utf-8 -*-
"""
واجهات المستخدم - تجريدات MVP Pattern
فصل الواجهة عن منطق العمل حسب مبدأ Dependency Inversion
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from pathlib import Path


class IMainView(ABC):
    """تجريد الواجهة الرئيسية - View في MVP"""
    
    @abstractmethod
    def show_message(self, title: str, message: str, message_type: str = "info") -> None:
        """عرض رسالة للمستخدم"""
        pass
    
    @abstractmethod
    def show_confirmation(self, title: str, message: str) -> bool:
        """عرض رسالة تأكيد"""
        pass
    
    @abstractmethod
    def update_progress(self, value: int, status: str, operation_type: str) -> None:
        """تحديث شريط التقدم"""
        pass
    
    @abstractmethod
    def toggle_controls(self, enable: bool, operation_type: str) -> None:
        """تفعيل/تعطيل عناصر التحكم"""
        pass
    
    @abstractmethod
    def get_selected_folders(self) -> List[Path]:
        """الحصول على المجلدات المحددة"""
        pass
    
    @abstractmethod
    def get_exclusions(self) -> List[str]:
        """الحصول على قائمة الاستثناءات"""
        pass
    
    @abstractmethod
    def get_selected_backup(self) -> Optional[Path]:
        """الحصول على النسخة المحددة للاسترداد"""
        pass
    
    @abstractmethod
    def get_selected_backups_for_deletion(self) -> List[Path]:
        """الحصول على النسخ المحددة للحذف"""
        pass
    
    @abstractmethod
    def get_retention_count(self) -> int:
        """الحصول على عدد النسخ المراد الاحتفاظ بها"""
        pass
    
    @abstractmethod
    def refresh_backups_list(self) -> None:
        """تحديث قائمة النسخ الاحتياطية"""
        pass


class IMainPresenter(ABC):
    """تجريد المقدم الرئيسي - Presenter في MVP"""
    
    @abstractmethod
    def start_backup(self) -> None:
        """بدء عملية النسخ الاحتياطي"""
        pass
    
    @abstractmethod
    def start_restore(self) -> None:
        """بدء عملية الاسترداد"""
        pass
    
    @abstractmethod
    def cancel_operation(self) -> None:
        """إلغاء العملية الجارية"""
        pass
    
    @abstractmethod
    def delete_backups(self) -> None:
        """حذف النسخ المحددة"""
        pass
    
    @abstractmethod
    def add_custom_folder(self, folder_path: str) -> None:
        """إضافة مجلد مخصص"""
        pass
    
    @abstractmethod
    def remove_custom_folder(self) -> None:
        """إزالة مجلد مخصص"""
        pass
    
    @abstractmethod
    def add_exclusion(self, exclusion_pattern: str) -> None:
        """إضافة استثناء"""
        pass
    
    @abstractmethod
    def remove_exclusion(self) -> None:
        """إزالة استثناء"""
        pass
    
    @abstractmethod
    def refresh_backups(self) -> None:
        """تحديث قائمة النسخ"""
        pass


class IBackupModel(ABC):
    """تجريد نموذج البيانات - Model في MVP"""
    
    @abstractmethod
    def get_available_backups(self) -> List[Path]:
        """الحصول على النسخ المتاحة"""
        pass
    
    @abstractmethod
    def delete_backups(self, backup_paths: List[Path]) -> int:
        """حذف النسخ المحددة"""
        pass
    
    @abstractmethod
    def apply_backup_rotation(self, retention_count: int) -> int:
        """تطبيق دوران النسخ"""
        pass
    
    @abstractmethod
    def get_exclusions(self) -> List[str]:
        """الحصول على قائمة الاستثناءات"""
        pass
    
    @abstractmethod
    def save_exclusions(self, exclusions: List[str]) -> None:
        """حفظ قائمة الاستثناءات"""
        pass
    
    @abstractmethod
    def get_default_folders(self) -> List[Path]:
        """الحصول على المجلدات الافتراضية"""
        pass