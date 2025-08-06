# -*- coding: utf-8 -*-
"""
مدير الإعدادات المتقدم - Configuration Manager
مسؤولية واحدة: إدارة إعدادات التطبيق مع التحقق من الصحة
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

from core.logging_system import ILogger, LoggerFactory
from utils.config import APP_DIR


@dataclass
class AppSettings:
    """إعدادات التطبيق - Value Object"""
    backup_retention: int = 5
    default_exclusions: List[str] = None
    auto_backup_enabled: bool = False
    auto_backup_interval_hours: int = 24
    compression_level: int = 6
    max_backup_size_mb: int = 1000
    enable_logging: bool = True
    log_level: str = "INFO"
    theme: str = "dark"
    language: str = "ar"
    
    def __post_init__(self):
        if self.default_exclusions is None:
            self.default_exclusions = [
                "*.tmp", "*.log", "*.cache", "__pycache__", 
                ".git", "node_modules", "*.pyc"
            ]


class ConfigurationValidator:
    """مُحقق صحة الإعدادات - Single Responsibility"""
    
    @staticmethod
    def validate_backup_retention(value: int) -> bool:
        """التحقق من صحة عدد النسخ المحتفظ بها"""
        return isinstance(value, int) and 1 <= value <= 100
    
    @staticmethod
    def validate_compression_level(value: int) -> bool:
        """التحقق من صحة مستوى الضغط"""
        return isinstance(value, int) and 0 <= value <= 9
    
    @staticmethod
    def validate_max_backup_size(value: int) -> bool:
        """التحقق من صحة الحد الأقصى لحجم النسخة"""
        return isinstance(value, int) and value > 0
    
    @staticmethod
    def validate_auto_backup_interval(value: int) -> bool:
        """التحقق من صحة فترة النسخ التلقائي"""
        return isinstance(value, int) and 1 <= value <= 168  # أسبوع كحد أقصى
    
    @staticmethod
    def validate_log_level(value: str) -> bool:
        """التحقق من صحة مستوى السجلات"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        return isinstance(value, str) and value.upper() in valid_levels
    
    @staticmethod
    def validate_theme(value: str) -> bool:
        """التحقق من صحة السمة"""
        valid_themes = ["dark", "light"]
        return isinstance(value, str) and value.lower() in valid_themes
    
    @staticmethod
    def validate_language(value: str) -> bool:
        """التحقق من صحة اللغة"""
        valid_languages = ["ar", "en"]
        return isinstance(value, str) and value.lower() in valid_languages


class ConfigurationManager:
    """مدير الإعدادات - مسؤولية إدارة الإعدادات مع التحقق من الصحة"""
    
    def __init__(self, 
                 config_file: str = "app_settings.json",
                 logger: ILogger = None):
        self.config_path = APP_DIR / config_file
        self.logger = logger or LoggerFactory.create_default_logger()
        self.validator = ConfigurationValidator()
        self._settings = None
        
        # التأكد من وجود مجلد الإعدادات
        self._ensure_config_directory()
    
    def _ensure_config_directory(self) -> None:
        """التأكد من وجود مجلد الإعدادات"""
        try:
            APP_DIR.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            self.logger.error(f"فشل في إنشاء مجلد الإعدادات: {e}")
            raise
    
    def load_settings(self) -> AppSettings:
        """تحميل الإعدادات من الملف"""
        if self._settings is not None:
            return self._settings
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # التحقق من صحة البيانات المحملة
                validated_data = self._validate_loaded_data(data)
                self._settings = AppSettings(**validated_data)
                
                self.logger.info("تم تحميل الإعدادات بنجاح")
            else:
                # إنشاء إعدادات افتراضية
                self._settings = AppSettings()
                self.save_settings(self._settings)
                self.logger.info("تم إنشاء إعدادات افتراضية")
            
            return self._settings
            
        except Exception as e:
            self.logger.error(f"فشل في تحميل الإعدادات: {e}")
            # إرجاع إعدادات افتراضية في حالة الفشل
            self._settings = AppSettings()
            return self._settings
    
    def save_settings(self, settings: AppSettings) -> bool:
        """حفظ الإعدادات إلى الملف"""
        try:
            # التحقق من صحة الإعدادات قبل الحفظ
            if not self._validate_settings(settings):
                self.logger.error("فشل في التحقق من صحة الإعدادات")
                return False
            
            # تحويل إلى قاموس وحفظ
            settings_dict = asdict(settings)
            
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(settings_dict, f, indent=2, ensure_ascii=False)
            
            # تحديث التخزين المؤقت
            self._settings = settings
            
            self.logger.info("تم حفظ الإعدادات بنجاح")
            return True
            
        except Exception as e:
            self.logger.error(f"فشل في حفظ الإعدادات: {e}")
            return False
    
    def update_setting(self, key: str, value: Any) -> bool:
        """تحديث إعداد واحد"""
        try:
            current_settings = self.load_settings()
            
            # التحقق من وجود المفتاح
            if not hasattr(current_settings, key):
                self.logger.error(f"مفتاح الإعداد غير موجود: {key}")
                return False
            
            # إنشاء إعدادات جديدة مع القيمة المحدثة
            settings_dict = asdict(current_settings)
            settings_dict[key] = value
            
            new_settings = AppSettings(**settings_dict)
            
            return self.save_settings(new_settings)
            
        except Exception as e:
            self.logger.error(f"فشل في تحديث الإعداد {key}: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """الحصول على قيمة إعداد واحد"""
        try:
            settings = self.load_settings()
            return getattr(settings, key, default)
        except Exception as e:
            self.logger.error(f"فشل في الحصول على الإعداد {key}: {e}")
            return default
    
    def reset_to_defaults(self) -> bool:
        """إعادة تعيين الإعدادات إلى القيم الافتراضية"""
        try:
            default_settings = AppSettings()
            success = self.save_settings(default_settings)
            
            if success:
                self.logger.info("تم إعادة تعيين الإعدادات إلى القيم الافتراضية")
            
            return success
            
        except Exception as e:
            self.logger.error(f"فشل في إعادة تعيين الإعدادات: {e}")
            return False
    
    def export_settings(self, export_path: Path) -> bool:
        """تصدير الإعدادات إلى ملف"""
        try:
            settings = self.load_settings()
            settings_dict = asdict(settings)
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(settings_dict, f, indent=2, ensure_ascii=False)
            
            self.logger.info(f"تم تصدير الإعدادات إلى: {export_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"فشل في تصدير الإعدادات: {e}")
            return False
    
    def import_settings(self, import_path: Path) -> bool:
        """استيراد الإعدادات من ملف"""
        try:
            if not import_path.exists():
                self.logger.error(f"ملف الاستيراد غير موجود: {import_path}")
                return False
            
            with open(import_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # التحقق من صحة البيانات المستوردة
            validated_data = self._validate_loaded_data(data)
            new_settings = AppSettings(**validated_data)
            
            success = self.save_settings(new_settings)
            
            if success:
                self.logger.info(f"تم استيراد الإعدادات من: {import_path}")
            
            return success
            
        except Exception as e:
            self.logger.error(f"فشل في استيراد الإعدادات: {e}")
            return False
    
    def _validate_settings(self, settings: AppSettings) -> bool:
        """التحقق من صحة جميع الإعدادات"""
        validations = [
            self.validator.validate_backup_retention(settings.backup_retention),
            self.validator.validate_compression_level(settings.compression_level),
            self.validator.validate_max_backup_size(settings.max_backup_size_mb),
            self.validator.validate_auto_backup_interval(settings.auto_backup_interval_hours),
            self.validator.validate_log_level(settings.log_level),
            self.validator.validate_theme(settings.theme),
            self.validator.validate_language(settings.language),
        ]
        
        return all(validations)
    
    def _validate_loaded_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """التحقق من صحة البيانات المحملة وتصحيحها"""
        validated_data = {}
        default_settings = AppSettings()
        
        # التحقق من كل حقل وتصحيحه إذا لزم الأمر
        for field_name, default_value in asdict(default_settings).items():
            if field_name in data:
                value = data[field_name]
                
                # التحقق من صحة القيمة حسب النوع
                if field_name == "backup_retention" and self.validator.validate_backup_retention(value):
                    validated_data[field_name] = value
                elif field_name == "compression_level" and self.validator.validate_compression_level(value):
                    validated_data[field_name] = value
                elif field_name == "max_backup_size_mb" and self.validator.validate_max_backup_size(value):
                    validated_data[field_name] = value
                elif field_name == "auto_backup_interval_hours" and self.validator.validate_auto_backup_interval(value):
                    validated_data[field_name] = value
                elif field_name == "log_level" and self.validator.validate_log_level(value):
                    validated_data[field_name] = value.upper()
                elif field_name == "theme" and self.validator.validate_theme(value):
                    validated_data[field_name] = value.lower()
                elif field_name == "language" and self.validator.validate_language(value):
                    validated_data[field_name] = value.lower()
                elif isinstance(value, type(default_value)):
                    validated_data[field_name] = value
                else:
                    self.logger.warning(f"قيمة غير صحيحة للحقل {field_name}: {value}, استخدام القيمة الافتراضية")
                    validated_data[field_name] = default_value
            else:
                validated_data[field_name] = default_value
        
        return validated_data