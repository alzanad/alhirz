"""
نظام السجلات المتقدم للحِرز
مسؤولية واحدة: إدارة وتسجيل الأحداث والأخطاء
"""
import os
import json
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, Any, Optional, List

from utils.config import APP_DIR


class LogLevel(Enum):
    """مستويات السجلات"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class ILogger(ABC):
    """تجريد نظام السجلات - Interface Segregation Principle"""
    
    @abstractmethod
    def log(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """تسجيل رسالة"""
        pass
    
    @abstractmethod
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """تسجيل رسالة تشخيص"""
        pass
    
    @abstractmethod
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """تسجيل رسالة معلوماتية"""
        pass
    
    @abstractmethod
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """تسجيل تحذير"""
        pass
    
    @abstractmethod
    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """تسجيل خطأ"""
        pass
    
    @abstractmethod
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """تسجيل خطأ حرج"""
        pass


class LogEntry:
    """كائن يمثل إدخال سجل واحد"""
    
    def __init__(self, 
                 level: LogLevel, 
                 message: str, 
                 context: Optional[Dict[str, Any]] = None,
                 timestamp: Optional[datetime] = None):
        self.level = level
        self.message = message
        self.context = context or {}
        self.timestamp = timestamp or datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """تحويل إلى قاموس"""
        return {
            'timestamp': self.timestamp.isoformat(),
            'level': self.level.value,
            'message': self.message,
            'context': self.context
        }
    
    def to_string(self) -> str:
        """تحويل إلى نص"""
        timestamp_str = self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        context_str = f" | {json.dumps(self.context, ensure_ascii=False)}" if self.context else ""
        return f"[{timestamp_str}] {self.level.value}: {self.message}{context_str}"


class FileLogger(ILogger):
    """مسجل الملفات - مسؤولية واحدة: كتابة السجلات في ملف"""
    
    def __init__(self, 
                 log_file_path: Path = None, 
                 min_level: LogLevel = LogLevel.INFO,
                 max_file_size_mb: int = 10,
                 max_files: int = 5):
        self.log_file_path = log_file_path or (APP_DIR / "logs" / "alhirz.log")
        self.min_level = min_level
        self.max_file_size_mb = max_file_size_mb
        self.max_files = max_files
        
        # إنشاء مجلد السجلات إذا لم يكن موجوداً
        self.log_file_path.parent.mkdir(parents=True, exist_ok=True)
    
    def log(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """تسجيل رسالة في الملف"""
        if self._should_log(level):
            entry = LogEntry(level, message, context)
            self._write_to_file(entry)
            self._rotate_logs_if_needed()
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.DEBUG, message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.INFO, message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.WARNING, message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.ERROR, message, context)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.CRITICAL, message, context)
    
    def _should_log(self, level: LogLevel) -> bool:
        """فحص ما إذا كان يجب تسجيل هذا المستوى"""
        level_values = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4
        }
        return level_values[level] >= level_values[self.min_level]
    
    def _write_to_file(self, entry: LogEntry) -> None:
        """كتابة الإدخال في الملف"""
        try:
            with open(self.log_file_path, 'a', encoding='utf-8') as f:
                f.write(entry.to_string() + '\n')
        except Exception:
            # في حالة فشل الكتابة، لا نريد أن نتسبب في خطأ آخر
            pass
    
    def _rotate_logs_if_needed(self) -> None:
        """تدوير السجلات إذا تجاوز الحجم المحدد"""
        try:
            if not self.log_file_path.exists():
                return
            
            file_size_mb = self.log_file_path.stat().st_size / (1024 * 1024)
            
            if file_size_mb > self.max_file_size_mb:
                self._rotate_logs()
        except Exception:
            pass
    
    def _rotate_logs(self) -> None:
        """تدوير ملفات السجلات"""
        try:
            # نقل الملفات الموجودة
            for i in range(self.max_files - 1, 0, -1):
                old_file = self.log_file_path.with_suffix(f'.{i}.log')
                new_file = self.log_file_path.with_suffix(f'.{i + 1}.log')
                
                if old_file.exists():
                    if new_file.exists():
                        new_file.unlink()
                    old_file.rename(new_file)
            
            # نقل الملف الحالي
            if self.log_file_path.exists():
                rotated_file = self.log_file_path.with_suffix('.1.log')
                if rotated_file.exists():
                    rotated_file.unlink()
                self.log_file_path.rename(rotated_file)
        except Exception:
            pass


class ConsoleLogger(ILogger):
    """مسجل وحدة التحكم - مسؤولية واحدة: عرض السجلات في وحدة التحكم"""
    
    def __init__(self, min_level: LogLevel = LogLevel.INFO):
        self.min_level = min_level
    
    def log(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """تسجيل رسالة في وحدة التحكم"""
        if self._should_log(level):
            entry = LogEntry(level, message, context)
            print(entry.to_string())
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.DEBUG, message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.INFO, message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.WARNING, message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.ERROR, message, context)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        self.log(LogLevel.CRITICAL, message, context)
    
    def _should_log(self, level: LogLevel) -> bool:
        """فحص ما إذا كان يجب تسجيل هذا المستوى"""
        level_values = {
            LogLevel.DEBUG: 0,
            LogLevel.INFO: 1,
            LogLevel.WARNING: 2,
            LogLevel.ERROR: 3,
            LogLevel.CRITICAL: 4
        }
        return level_values[level] >= level_values[self.min_level]


class CompositeLogger(ILogger):
    """مسجل مركب - يجمع عدة مسجلات - Composite Pattern"""
    
    def __init__(self, loggers: List[ILogger] = None):
        self.loggers = loggers or []
    
    def add_logger(self, logger: ILogger) -> None:
        """إضافة مسجل جديد"""
        self.loggers.append(logger)
    
    def remove_logger(self, logger: ILogger) -> None:
        """إزالة مسجل"""
        if logger in self.loggers:
            self.loggers.remove(logger)
    
    def log(self, level: LogLevel, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        """تسجيل في جميع المسجلات"""
        for logger in self.loggers:
            logger.log(level, message, context)
    
    def debug(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        for logger in self.loggers:
            logger.debug(message, context)
    
    def info(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        for logger in self.loggers:
            logger.info(message, context)
    
    def warning(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        for logger in self.loggers:
            logger.warning(message, context)
    
    def error(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        for logger in self.loggers:
            logger.error(message, context)
    
    def critical(self, message: str, context: Optional[Dict[str, Any]] = None) -> None:
        for logger in self.loggers:
            logger.critical(message, context)


class LoggerFactory:
    """Factory لإنشاء المسجلات - Factory Pattern"""
    
    @staticmethod
    def create_default_logger() -> ILogger:
        """إنشاء المسجل الافتراضي للنظام - يسجل الأخطاء فقط"""
        file_logger = FileLogger(min_level=LogLevel.ERROR)
        console_logger = ConsoleLogger(min_level=LogLevel.ERROR)
        
        composite_logger = CompositeLogger()
        composite_logger.add_logger(file_logger)
        composite_logger.add_logger(console_logger)
        
        return composite_logger
    
    @staticmethod
    def create_debug_logger() -> ILogger:
        """إنشاء مسجل للتشخيص"""
        file_logger = FileLogger(min_level=LogLevel.DEBUG)
        console_logger = ConsoleLogger(min_level=LogLevel.DEBUG)
        
        composite_logger = CompositeLogger()
        composite_logger.add_logger(file_logger)
        composite_logger.add_logger(console_logger)
        
        return composite_logger
    
    @staticmethod
    def create_file_only_logger() -> ILogger:
        """إنشاء مسجل للملفات فقط"""
        return FileLogger(min_level=LogLevel.INFO)
    
    @staticmethod
    def create_console_only_logger() -> ILogger:
        """إنشاء مسجل لوحدة التحكم فقط"""
        return ConsoleLogger(min_level=LogLevel.INFO)