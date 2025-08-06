# -*- coding: utf-8 -*-
"""
نموذج البيانات للواجهة - Model في MVP Pattern
مسؤولية واحدة: إدارة البيانات والحالة
"""

import json
from pathlib import Path
from typing import List

from interfaces.ui_interfaces import IBackupModel
from utils.config import (APP_DIR, BACKUP_DIR, HOME_DIR, DEFAULT_FOLDERS,
                          SETTINGS_FILENAME, DEFAULT_EXCLUSIONS)
from core.backup_manager import BackupManager
from core.logging_system import ILogger, LoggerFactory


class BackupModel(IBackupModel):
    """نموذج البيانات - مسؤولية إدارة البيانات فقط"""
    
    def __init__(self, 
                 backup_manager: BackupManager = None,
                 logger: ILogger = None):
        self.backup_manager = backup_manager or BackupManager()
        self.logger = logger or LoggerFactory.create_default_logger()
        self._exclusions_cache = None
        
        # التأكد من وجود المجلدات المطلوبة
        self._ensure_directories()
    
    def _ensure_directories(self) -> None:
        """التأكد من وجود المجلدات المطلوبة"""
        try:
            BACKUP_DIR.mkdir(parents=True, exist_ok=True)
            APP_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self.logger.error(f"فشل في إنشاء المجلدات: {e}")
            raise
    
    def get_available_backups(self) -> List[Path]:
        """الحصول على النسخ المتاحة مرتبة حسب التاريخ"""
        try:
            return self.backup_manager.get_backups_list()
        except Exception as e:
            self.logger.error(f"فشل في الحصول على قائمة النسخ: {e}")
            return []
    
    def delete_backups(self, backup_paths: List[Path]) -> int:
        """حذف النسخ المحددة وإرجاع عدد المحذوفة"""
        try:
            return self.backup_manager.delete_backups(backup_paths)
        except Exception as e:
            self.logger.error(f"فشل في حذف النسخ: {e}")
            return 0
    
    def apply_backup_rotation(self, retention_count: int) -> int:
        """تطبيق دوران النسخ وإرجاع عدد المحذوفة"""
        try:
            return self.backup_manager.apply_backup_rotation(retention_count)
        except Exception as e:
            self.logger.error(f"فشل في تطبيق دوران النسخ: {e}")
            return 0
    
    def get_settings(self) -> dict:
        """الحصول على جميع الإعدادات"""
        settings_path = APP_DIR / SETTINGS_FILENAME
        
        try:
            if settings_path.exists():
                with open(settings_path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            else:
                settings = {
                    'exclusions': DEFAULT_EXCLUSIONS.copy(),
                    'selected_folders': [],
                    'ignore_hidden_files': True
                }
                self.save_settings(settings)
            
            return settings
            
        except Exception as e:
            self.logger.error(f"فشل في قراءة الإعدادات: {e}")
            return {
                'exclusions': DEFAULT_EXCLUSIONS.copy(),
                'selected_folders': [],
                'ignore_hidden_files': True
            }
    
    def save_settings(self, settings: dict) -> None:
        """حفظ جميع الإعدادات"""
        settings_path = APP_DIR / SETTINGS_FILENAME
        
        try:
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
            
            # تحديث التخزين المؤقت
            self._exclusions_cache = settings.get('exclusions', []).copy()
            
        except Exception as e:
            self.logger.error(f"فشل في حفظ الإعدادات: {e}")
            raise
    
    def get_exclusions(self) -> List[str]:
        """الحصول على قائمة الاستثناءات"""
        settings = self.get_settings()
        return settings.get('exclusions', DEFAULT_EXCLUSIONS.copy())
    
    def save_exclusions(self, exclusions: List[str]) -> None:
        """حفظ قائمة الاستثناءات"""
        settings = self.get_settings()
        settings['exclusions'] = exclusions
        self.save_settings(settings)
    
    def get_selected_folders(self) -> List[str]:
        """الحصول على المجلدات المحددة"""
        settings = self.get_settings()
        return settings.get('selected_folders', [])
    
    def save_selected_folders(self, folders: List[str]) -> None:
        """حفظ المجلدات المحددة"""
        settings = self.get_settings()
        settings['selected_folders'] = folders
        self.save_settings(settings)
    
    def get_ignore_hidden_files(self) -> bool:
        """الحصول على إعداد تجاهل الملفات المخفية"""
        settings = self.get_settings()
        return settings.get('ignore_hidden_files', True)
    
    def set_ignore_hidden_files(self, ignore: bool) -> None:
        """تعيين إعداد تجاهل الملفات المخفية"""
        settings = self.get_settings()
        settings['ignore_hidden_files'] = ignore
        self.save_settings(settings)
    
    def save_folder_settings(self, folders_settings: list) -> None:
        """حفظ إعدادات المجلدات"""
        settings = self.get_settings()
        settings['folders'] = folders_settings
        self.save_settings(settings)
    
    def get_folder_settings(self) -> list:
        """الحصول على إعدادات المجلدات"""
        settings = self.get_settings()
        return settings.get('folders', [])
    
    def get_default_folders(self) -> List[Path]:
        """الحصول على المجلدات الافتراضية الموجودة"""
        default_folders = []
        
        for folder_name in DEFAULT_FOLDERS:
            folder_path = HOME_DIR / folder_name
            if folder_path.is_dir():
                default_folders.append(folder_path)
        
        return default_folders
    
    def add_exclusion(self, exclusion_pattern: str) -> bool:
        """إضافة استثناء جديد"""
        if not exclusion_pattern.strip():
            return False
        
        exclusions = self.get_exclusions()
        
        if exclusion_pattern not in exclusions:
            exclusions.append(exclusion_pattern)
            self.save_exclusions(exclusions)
            return True
        
        return False
    
    def remove_exclusion(self, exclusion_pattern: str) -> bool:
        """إزالة استثناء"""
        exclusions = self.get_exclusions()
        
        if exclusion_pattern in exclusions:
            exclusions.remove(exclusion_pattern)
            self.save_exclusions(exclusions)
            return True
        
        return False
    
    def validate_folder_path(self, folder_path: Path) -> bool:
        """التحقق من صحة مسار المجلد"""
        return folder_path.exists() and folder_path.is_dir()
    
    def is_folder_already_added(self, folder_path: Path, existing_folders: List[Path]) -> bool:
        """التحقق من وجود المجلد مسبقاً"""
        return folder_path in existing_folders