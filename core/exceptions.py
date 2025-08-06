"""
استثناءات مخصصة لمجال النسخ الاحتياطي
مسؤولية واحدة: تعريف أنواع الأخطاء المختلفة في النظام
"""

from enum import Enum
from typing import Optional, Dict, Any


class ErrorSeverity(Enum):
    """مستويات خطورة الأخطاء"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ErrorCategory(Enum):
    """فئات الأخطاء"""
    FILE_SYSTEM = "file_system"
    BACKUP_OPERATION = "backup_operation"
    RESTORE_OPERATION = "restore_operation"
    VALIDATION = "validation"
    CONFIGURATION = "configuration"
    NETWORK = "network"


class AlHirzException(Exception):
    """الاستثناء الأساسي لجميع أخطاء النظام"""
    
    def __init__(self, 
                 message: str,
                 category: ErrorCategory,
                 severity: ErrorSeverity = ErrorSeverity.MEDIUM,
                 context: Optional[Dict[str, Any]] = None,
                 recoverable: bool = True):
        super().__init__(message)
        self.message = message
        self.category = category
        self.severity = severity
        self.context = context or {}
        self.recoverable = recoverable
    
    def __str__(self) -> str:
        return f"[{self.category.value.upper()}] {self.message}"


class FileSystemException(AlHirzException):
    """أخطاء نظام الملفات"""
    
    def __init__(self, message: str, file_path: str = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.FILE_SYSTEM,
            **kwargs
        )
        if file_path:
            self.context['file_path'] = file_path


class BackupException(AlHirzException):
    """أخطاء عمليات النسخ الاحتياطي"""
    
    def __init__(self, message: str, backup_path: str = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.BACKUP_OPERATION,
            **kwargs
        )
        if backup_path:
            self.context['backup_path'] = backup_path


class RestoreException(AlHirzException):
    """أخطاء عمليات الاسترداد"""
    
    def __init__(self, message: str, restore_path: str = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.RESTORE_OPERATION,
            **kwargs
        )
        if restore_path:
            self.context['restore_path'] = restore_path


class ValidationException(AlHirzException):
    """أخطاء التحقق من صحة البيانات"""
    
    def __init__(self, message: str, field_name: str = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.VALIDATION,
            severity=ErrorSeverity.HIGH,
            recoverable=False,
            **kwargs
        )
        if field_name:
            self.context['field_name'] = field_name


class ConfigurationException(AlHirzException):
    """أخطاء الإعدادات"""
    
    def __init__(self, message: str, config_key: str = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.CONFIGURATION,
            severity=ErrorSeverity.HIGH,
            **kwargs
        )
        if config_key:
            self.context['config_key'] = config_key


class NetworkException(AlHirzException):
    """أخطاء الشبكة (للمستقبل - التخزين السحابي)"""
    
    def __init__(self, message: str, endpoint: str = None, **kwargs):
        super().__init__(
            message=message,
            category=ErrorCategory.NETWORK,
            **kwargs
        )
        if endpoint:
            self.context['endpoint'] = endpoint


# استثناءات محددة للعمليات الشائعة

class FileNotFoundError(FileSystemException):
    """ملف غير موجود"""
    
    def __init__(self, file_path: str):
        super().__init__(
            message=f"الملف غير موجود: {file_path}",
            file_path=file_path,
            severity=ErrorSeverity.HIGH
        )


class InsufficientSpaceError(FileSystemException):
    """مساحة تخزين غير كافية"""
    
    def __init__(self, required_space: int, available_space: int):
        super().__init__(
            message=f"مساحة تخزين غير كافية. مطلوب: {required_space} MB، متاح: {available_space} MB",
            severity=ErrorSeverity.CRITICAL,
            recoverable=False
        )
        self.context.update({
            'required_space': required_space,
            'available_space': available_space
        })


class CorruptedBackupError(BackupException):
    """نسخة احتياطية تالفة"""
    
    def __init__(self, backup_path: str):
        super().__init__(
            message=f"النسخة الاحتياطية تالفة أو غير قابلة للقراءة: {backup_path}",
            backup_path=backup_path,
            severity=ErrorSeverity.HIGH,
            recoverable=False
        )


class BackupInterruptedError(BackupException):
    """تم إيقاف عملية النسخ"""
    
    def __init__(self, reason: str = "تم إلغاء العملية من قبل المستخدم"):
        super().__init__(
            message=f"تم إيقاف عملية النسخ: {reason}",
            severity=ErrorSeverity.LOW,
            recoverable=True
        )


class RestoreConflictError(RestoreException):
    """تعارض في عملية الاسترداد"""
    
    def __init__(self, conflicted_files: list):
        super().__init__(
            message=f"تعارض في {len(conflicted_files)} ملف أثناء الاسترداد",
            severity=ErrorSeverity.MEDIUM
        )
        self.context['conflicted_files'] = conflicted_files