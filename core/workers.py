
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Callable, Protocol

from PyQt5.QtCore import QThread, pyqtSignal

from interfaces.backup_interfaces import IBackupOrchestrator
from core.backup_manager import BackupOrchestrator
from core.logging_system import ILogger, LoggerFactory
from core.error_handler import ErrorHandler, ErrorHandlerFactory
from core.exceptions import AlHirzException, BackupInterruptedError


class IWorkerOperation(Protocol):
    """تجريد عمليات العامل - فصل التجريد عن التنفيذ"""
    
    def prepare(self) -> None:
        """التحضير للعملية"""
        ...
    
    def execute_operation(self) -> str:
        """تنفيذ العملية الأساسية"""
        ...
    
    def finalize(self, result: str) -> None:
        """إنهاء العملية وإرسال النتيجة"""
        ...
    
    def handle_cancellation(self) -> None:
        """معالجة إلغاء العملية"""
        ...
    
    def handle_error(self, error: Exception) -> None:
        """معالجة الأخطاء"""
        ...
    
    def get_error_context(self) -> dict:
        """الحصول على سياق الخطأ للمعالجة"""
        ...


class BaseWorker(QThread):
    """عامل أساسي موحد - Template Method Pattern مع دعم السجلات ومعالجة الأخطاء"""
    progress_update = pyqtSignal(int, str)
    finished = pyqtSignal(str)
    error_occurred = pyqtSignal(str, str)  # (error_message, error_category)
    
    def __init__(self, 
                 orchestrator: IBackupOrchestrator = None,
                 logger: ILogger = None,
                 error_handler: ErrorHandler = None):
        super().__init__()
        self.orchestrator = orchestrator or BackupOrchestrator()
        self.logger = logger or LoggerFactory.create_default_logger()
        self.error_handler = error_handler or ErrorHandlerFactory.create_default_handler()
        self.is_running = True
        self.operation_name = self.__class__.__name__
    
    def run(self):
        """Template Method - تدفق العمل الموحد مع معالجة الأخطاء والسجلات"""
        self.logger.info(f"بدء تشغيل {self.operation_name}")
        
        try:
            self.prepare()
            result = self.execute_operation()
            
            if not self.is_running:
                raise BackupInterruptedError("تم إلغاء العملية من قبل المستخدم")
            
            self.finalize(result)
            self.logger.info(f"اكتمل تشغيل {self.operation_name} بنجاح")
            
        except BackupInterruptedError as e:
            self.logger.warning(f"تم إلغاء {self.operation_name}: {e.message}")
            self.handle_cancellation()
        except Exception as e:
            self.logger.error(f"خطأ في {self.operation_name}: {str(e)}")
            
            # محاولة معالجة الخطأ باستخدام ErrorHandler
            context = self.get_error_context()
            if self.error_handler.handle_exception(e, context, self.operation_name):
                self.logger.info(f"تم الاسترداد من الخطأ في {self.operation_name}")
                # إعادة المحاولة
                try:
                    result = self.execute_operation()
                    self.finalize(result)
                    return
                except Exception as retry_error:
                    self.logger.error(f"فشل في إعادة المحاولة: {retry_error}")
            
            self.handle_error(e)
    
    def prepare(self) -> None:
        """التحضير للعملية - يمكن إعادة تعريفها في الفئات المشتقة"""
        pass
    
    def execute_operation(self) -> str:
        """تنفيذ العملية الأساسية - يجب إعادة تعريفها في الفئات المشتقة"""
        raise NotImplementedError("يجب تنفيذ execute_operation في الفئة المشتقة")
    
    def finalize(self, result: str) -> None:
        """إنهاء العملية وإرسال النتيجة - يجب إعادة تعريفها في الفئات المشتقة"""
        raise NotImplementedError("يجب تنفيذ finalize في الفئة المشتقة")
    
    def handle_cancellation(self) -> None:
        """معالجة إلغاء العملية - يجب إعادة تعريفها في الفئات المشتقة"""
        raise NotImplementedError("يجب تنفيذ handle_cancellation في الفئة المشتقة")
    
    def handle_error(self, error: Exception) -> None:
        """معالجة الأخطاء - يجب إعادة تعريفها في الفئات المشتقة"""
        raise NotImplementedError("يجب تنفيذ handle_error في الفئة المشتقة")
    
    def progress_callback(self, progress: int, message: str) -> None:
        """callback للتقدم"""
        self.progress_update.emit(progress, message)
    
    def stop(self) -> None:
        """إيقاف العملية"""
        self.is_running = False
        self.logger.info(f"تم طلب إيقاف {self.operation_name}")
    
    def get_error_context(self) -> dict:
        """الحصول على سياق الخطأ للمعالجة"""
        return {
            'worker_type': self.__class__.__name__,
            'operation_name': self.operation_name,
            'is_running': self.is_running
        }


class BackupWorker(BaseWorker):
    """عامل النسخ الاحتياطي - مسؤولية واحدة: تنفيذ النسخ في خيط منفصل"""
    
    def __init__(self, 
                 folders_to_backup: List[Path], 
                 backup_filepath: Path, 
                 exclusions: List[str],
                 orchestrator: IBackupOrchestrator = None,
                 logger: ILogger = None,
                 error_handler: ErrorHandler = None):
        super().__init__(orchestrator, logger, error_handler)
        self.folders_to_backup = folders_to_backup
        self.backup_filepath = backup_filepath
        self.exclusions = exclusions
        self.operation_name = "النسخ الاحتياطي"
    
    def prepare(self) -> None:
        """التحضير لعملية النسخ"""
        pass
    
    def execute_operation(self) -> str:
        """تنفيذ عملية النسخ"""
        self.orchestrator.create_incremental_backup(
            self.folders_to_backup,
            self.backup_filepath,
            self.exclusions,
            self.progress_callback,
            lambda: self.is_running
        )
        
        # التحقق من وجود الملف وحساب الحجم
        if not self.backup_filepath.exists():
            return "اكتمل النسخ بنجاح!\nلم يتم العثور على ملفات جديدة لنسخها."
        
        final_size_mb = self.backup_filepath.stat().st_size / (1024 * 1024)
        return f"اكتمل النسخ بنجاح!\nالمسار: {self.backup_filepath}\nالحجم: {final_size_mb:.2f} ميجابايت"
    
    def finalize(self, result: str) -> None:
        """إنهاء عملية النسخ"""
        self.finished.emit(result)
    
    def handle_cancellation(self) -> None:
        """معالجة إلغاء النسخ"""
        if self.backup_filepath.exists():
            self.backup_filepath.unlink()
        self.finished.emit("تم إلغاء عملية النسخ الاحتياطي.")
    
    def handle_error(self, error: Exception) -> None:
        """معالجة أخطاء النسخ"""
        if self.backup_filepath.exists():
            self.backup_filepath.unlink()
        self.finished.emit(f"حدث خطأ فادح أثناء النسخ:\n{error}")


class RestoreWorker(BaseWorker):
    """عامل الاسترداد - مسؤولية واحدة: تنفيذ الاسترداد في خيط منفصل"""
    
    def __init__(self, 
                 backup_to_restore: Path,
                 orchestrator: IBackupOrchestrator = None,
                 logger: ILogger = None,
                 error_handler: ErrorHandler = None):
        super().__init__(orchestrator, logger, error_handler)
        self.backup_to_restore = backup_to_restore
        self.operation_name = "الاسترداد"
    
    def prepare(self) -> None:
        """التحضير لعملية الاسترداد"""
        pass
    
    def execute_operation(self) -> str:
        """تنفيذ عملية الاسترداد"""
        return self.orchestrator.restore_from_backup(
            self.backup_to_restore,
            self.progress_callback,
            lambda: self.is_running
        )
    
    def finalize(self, result: str) -> None:
        """إنهاء عملية الاسترداد"""
        self.finished.emit(result)
    
    def handle_cancellation(self) -> None:
        """معالجة إلغاء الاسترداد"""
        self.finished.emit("تم إلغاء عملية الاسترداد.")
    
    def handle_error(self, error: Exception) -> None:
        """معالجة أخطاء الاسترداد"""
        self.finished.emit(f"حدث خطأ فادح أثناء الاسترداد:\n{error}")
