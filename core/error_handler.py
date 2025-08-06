"""
معالج الأخطاء المركزي للحِرز
مسؤولية واحدة: معالجة الأخطاء واستراتيجيات الاسترداد
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable, List
from pathlib import Path
import time

from core.exceptions import (
    AlHirzException, ErrorSeverity, ErrorCategory,
    FileSystemException, BackupException, RestoreException,
    ValidationException, ConfigurationException
)
from core.logging_system import ILogger, LogLevel, LoggerFactory


class IRecoveryStrategy(ABC):
    """تجريد استراتيجية الاسترداد"""
    
    @abstractmethod
    def can_recover(self, exception: AlHirzException) -> bool:
        """فحص إمكانية الاسترداد من الخطأ"""
        pass
    
    @abstractmethod
    def recover(self, exception: AlHirzException, context: Dict[str, Any]) -> bool:
        """محاولة الاسترداد من الخطأ"""
        pass


class RetryRecoveryStrategy(IRecoveryStrategy):
    """استراتيجية إعادة المحاولة"""
    
    def __init__(self, max_retries: int = 3, delay_seconds: float = 1.0):
        self.max_retries = max_retries
        self.delay_seconds = delay_seconds
    
    def can_recover(self, exception: AlHirzException) -> bool:
        """فحص إمكانية إعادة المحاولة"""
        # يمكن إعادة المحاولة للأخطاء القابلة للاسترداد وليست حرجة
        return (exception.recoverable and 
                exception.severity != ErrorSeverity.CRITICAL and
                exception.category in [ErrorCategory.FILE_SYSTEM, ErrorCategory.NETWORK])
    
    def recover(self, exception: AlHirzException, context: Dict[str, Any]) -> bool:
        """محاولة الاسترداد بإعادة المحاولة"""
        operation = context.get('operation')
        if not operation or not callable(operation):
            return False
        
        for attempt in range(self.max_retries):
            try:
                time.sleep(self.delay_seconds * (attempt + 1))  # تأخير متزايد
                operation()
                return True
            except Exception:
                continue
        
        return False


class FallbackRecoveryStrategy(IRecoveryStrategy):
    """استراتيجية البديل"""
    
    def can_recover(self, exception: AlHirzException) -> bool:
        """فحص إمكانية استخدام البديل"""
        return (exception.recoverable and 
                exception.category in [ErrorCategory.FILE_SYSTEM, ErrorCategory.BACKUP_OPERATION])
    
    def recover(self, exception: AlHirzException, context: Dict[str, Any]) -> bool:
        """محاولة الاسترداد باستخدام البديل"""
        fallback_operation = context.get('fallback_operation')
        if not fallback_operation or not callable(fallback_operation):
            return False
        
        try:
            fallback_operation()
            return True
        except Exception:
            return False


class ErrorHandler:
    """معالج الأخطاء المركزي - مسؤولية واحدة: معالجة وتنسيق الاستجابة للأخطاء"""
    
    def __init__(self, logger: ILogger = None):
        self.logger = logger or LoggerFactory.create_default_logger()
        self.recovery_strategies: List[IRecoveryStrategy] = []
        self.error_callbacks: Dict[ErrorCategory, List[Callable]] = {}
        self._setup_default_strategies()
    
    def _setup_default_strategies(self) -> None:
        """إعداد استراتيجيات الاسترداد الافتراضية"""
        self.recovery_strategies.append(RetryRecoveryStrategy())
        self.recovery_strategies.append(FallbackRecoveryStrategy())
    
    def add_recovery_strategy(self, strategy: IRecoveryStrategy) -> None:
        """إضافة استراتيجية استرداد جديدة"""
        self.recovery_strategies.append(strategy)
    
    def register_error_callback(self, category: ErrorCategory, callback: Callable) -> None:
        """تسجيل callback لفئة خطأ معينة"""
        if category not in self.error_callbacks:
            self.error_callbacks[category] = []
        self.error_callbacks[category].append(callback)
    
    def handle_exception(self, 
                        exception: Exception, 
                        context: Optional[Dict[str, Any]] = None,
                        operation_name: str = "عملية غير محددة") -> bool:
        """معالجة الاستثناء الرئيسية"""
        context = context or {}
        
        # تحويل الاستثناء العادي إلى AlHirzException إذا لزم الأمر
        if not isinstance(exception, AlHirzException):
            exception = self._convert_to_alhirz_exception(exception)
        
        # تسجيل الخطأ
        self._log_exception(exception, operation_name, context)
        
        # تنفيذ callbacks المسجلة
        self._execute_callbacks(exception)
        
        # محاولة الاسترداد
        recovery_success = self._attempt_recovery(exception, context)
        
        # تسجيل نتيجة الاسترداد
        if recovery_success:
            self.logger.info(f"تم الاسترداد بنجاح من الخطأ في {operation_name}")
        else:
            self.logger.error(f"فشل الاسترداد من الخطأ في {operation_name}")
        
        return recovery_success
    
    def _convert_to_alhirz_exception(self, exception: Exception) -> AlHirzException:
        """تحويل الاستثناء العادي إلى AlHirzException"""
        if isinstance(exception, FileNotFoundError):
            return FileSystemException(
                message=f"ملف غير موجود: {str(exception)}",
                severity=ErrorSeverity.HIGH
            )
        elif isinstance(exception, PermissionError):
            return FileSystemException(
                message=f"ليس لديك صلاحية للوصول: {str(exception)}",
                severity=ErrorSeverity.HIGH
            )
        elif isinstance(exception, OSError):
            return FileSystemException(
                message=f"خطأ في نظام التشغيل: {str(exception)}",
                severity=ErrorSeverity.MEDIUM
            )
        else:
            return AlHirzException(
                message=str(exception),
                category=ErrorCategory.BACKUP_OPERATION,
                severity=ErrorSeverity.MEDIUM
            )
    
    def _log_exception(self, 
                      exception: AlHirzException, 
                      operation_name: str, 
                      context: Dict[str, Any]) -> None:
        """تسجيل الاستثناء"""
        log_context = {
            'operation': operation_name,
            'category': exception.category.value,
            'severity': exception.severity.value,
            'recoverable': exception.recoverable,
            'exception_context': exception.context,
            'handler_context': context
        }
        
        # اختيار مستوى السجل حسب خطورة الخطأ
        if exception.severity == ErrorSeverity.CRITICAL:
            self.logger.critical(exception.message, log_context)
        elif exception.severity == ErrorSeverity.HIGH:
            self.logger.error(exception.message, log_context)
        elif exception.severity == ErrorSeverity.MEDIUM:
            self.logger.warning(exception.message, log_context)
        else:
            self.logger.info(exception.message, log_context)
    
    def _execute_callbacks(self, exception: AlHirzException) -> None:
        """تنفيذ callbacks المسجلة لفئة الخطأ"""
        callbacks = self.error_callbacks.get(exception.category, [])
        for callback in callbacks:
            try:
                callback(exception)
            except Exception as callback_error:
                self.logger.error(f"خطأ في تنفيذ callback: {callback_error}")
    
    def _attempt_recovery(self, exception: AlHirzException, context: Dict[str, Any]) -> bool:
        """محاولة الاسترداد باستخدام الاستراتيجيات المتاحة"""
        if not exception.recoverable:
            return False
        
        for strategy in self.recovery_strategies:
            if strategy.can_recover(exception):
                try:
                    if strategy.recover(exception, context):
                        self.logger.info(f"نجح الاسترداد باستخدام {strategy.__class__.__name__}")
                        return True
                except Exception as recovery_error:
                    self.logger.warning(f"فشل في استراتيجية الاسترداد {strategy.__class__.__name__}: {recovery_error}")
        
        return False
    
    def create_safe_operation(self, operation: Callable, operation_name: str) -> Callable:
        """إنشاء عملية آمنة مع معالجة الأخطاء التلقائية"""
        def safe_operation(*args, **kwargs):
            try:
                return operation(*args, **kwargs)
            except Exception as e:
                context = {
                    'operation': operation,
                    'args': args,
                    'kwargs': kwargs
                }
                success = self.handle_exception(e, context, operation_name)
                if not success:
                    raise  # إعادة رفع الاستثناء إذا فشل الاسترداد
        
        return safe_operation


class ErrorHandlerFactory:
    """Factory لإنشاء معالجات الأخطاء"""
    
    @staticmethod
    def create_default_handler() -> ErrorHandler:
        """إنشاء معالج الأخطاء الافتراضي"""
        logger = LoggerFactory.create_default_logger()
        return ErrorHandler(logger)
    
    @staticmethod
    def create_debug_handler() -> ErrorHandler:
        """إنشاء معالج أخطاء للتشخيص"""
        logger = LoggerFactory.create_debug_logger()
        return ErrorHandler(logger)
    
    @staticmethod
    def create_silent_handler() -> ErrorHandler:
        """إنشاء معالج أخطاء صامت (للاختبارات)"""
        logger = LoggerFactory.create_file_only_logger()
        return ErrorHandler(logger)