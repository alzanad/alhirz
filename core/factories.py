from enum import Enum
from pathlib import Path
from typing import List, Dict, Any

from interfaces.backup_interfaces import IBackupStrategy, IRestoreStrategy, IBackupOrchestrator
from core.strategies import IncrementalBackupStrategy, SmartRestoreStrategy
from core.backup_manager import BackupOrchestrator
from core.workers import BackupWorker, RestoreWorker


class BackupType(Enum):
    """أنواع النسخ الاحتياطي المدعومة"""
    INCREMENTAL = "incremental"
    FULL = "full"


class RestoreType(Enum):
    """أنواع الاسترداد المدعومة"""
    SMART = "smart"
    OVERWRITE = "overwrite"


class BackupStrategyFactory:
    """Factory لإنشاء استراتيجيات النسخ - Open/Closed Principle"""
    
    @staticmethod
    def create_strategy(backup_type: BackupType, old_manifest: Dict[str, Any] = None) -> IBackupStrategy:
        """إنشاء استراتيجية النسخ المناسبة"""
        
        if backup_type == BackupType.INCREMENTAL:
            return IncrementalBackupStrategy(old_manifest or {})
        elif backup_type == BackupType.FULL:
            # يمكن إضافة FullBackupStrategy لاحقاً دون تعديل هذا الكود
            return IncrementalBackupStrategy({})  # مؤقتاً
        else:
            raise ValueError(f"نوع النسخ غير مدعوم: {backup_type}")


class RestoreStrategyFactory:
    """Factory لإنشاء استراتيجيات الاسترداد - Open/Closed Principle"""
    
    @staticmethod
    def create_strategy(restore_type: RestoreType) -> IRestoreStrategy:
        """إنشاء استراتيجية الاسترداد المناسبة"""
        
        if restore_type == RestoreType.SMART:
            return SmartRestoreStrategy()
        elif restore_type == RestoreType.OVERWRITE:
            # يمكن إضافة OverwriteRestoreStrategy لاحقاً دون تعديل هذا الكود
            return SmartRestoreStrategy()  # مؤقتاً
        else:
            raise ValueError(f"نوع الاسترداد غير مدعوم: {restore_type}")


class WorkerFactory:
    """Factory لإنشاء العمال - Dependency Inversion Principle"""
    
    @staticmethod
    def create_backup_worker(folders_to_backup: List[Path], 
                           backup_filepath: Path, 
                           exclusions: List[str],
                           orchestrator: IBackupOrchestrator = None) -> BackupWorker:
        """إنشاء عامل النسخ الاحتياطي"""
        
        if orchestrator is None:
            orchestrator = BackupOrchestrator()
        
        return BackupWorker(
            folders_to_backup=folders_to_backup,
            backup_filepath=backup_filepath,
            exclusions=exclusions,
            orchestrator=orchestrator
        )
    
    @staticmethod
    def create_restore_worker(backup_to_restore: Path,
                            orchestrator: IBackupOrchestrator = None) -> RestoreWorker:
        """إنشاء عامل الاسترداد"""
        
        if orchestrator is None:
            orchestrator = BackupOrchestrator()
        
        return RestoreWorker(
            backup_to_restore=backup_to_restore,
            orchestrator=orchestrator
        )


class ServiceContainer:
    """Container بسيط لإدارة الاعتماديات - Dependency Injection"""
    
    def __init__(self):
        self._services = {}
        self._setup_default_services()
    
    def _setup_default_services(self):
        """إعداد الخدمات الافتراضية"""
        from core.file_scanner import FileScanner
        from core.backup_repository import BackupRepository
        from core.logging_system import LoggerFactory
        from core.error_handler import ErrorHandlerFactory
        
        # إعداد نظام السجلات ومعالجة الأخطاء
        logger = LoggerFactory.create_default_logger()
        error_handler = ErrorHandlerFactory.create_default_handler()
        
        self.register('logger', logger)
        self.register('error_handler', error_handler)
        self.register('file_scanner', FileScanner())
        self.register('backup_repository', BackupRepository())
        self.register('backup_orchestrator', BackupOrchestrator(
            file_scanner=self.get('file_scanner'),
            repository=self.get('backup_repository'),
            logger=self.get('logger'),
            error_handler=self.get('error_handler')
        ))
    
    def register(self, name: str, service: Any) -> None:
        """تسجيل خدمة في الحاوية"""
        self._services[name] = service
    
    def get(self, name: str) -> Any:
        """الحصول على خدمة من الحاوية"""
        if name not in self._services:
            raise ValueError(f"الخدمة غير مسجلة: {name}")
        return self._services[name]
    
    def create_backup_worker(self, folders_to_backup: List[Path], 
                           backup_filepath: Path, 
                           exclusions: List[str]) -> BackupWorker:
        """إنشاء عامل النسخ باستخدام الاعتماديات المحقونة"""
        orchestrator = self.get('backup_orchestrator')
        return WorkerFactory.create_backup_worker(
            folders_to_backup, backup_filepath, exclusions, orchestrator
        )
    
    def create_restore_worker(self, backup_to_restore: Path) -> RestoreWorker:
        """إنشاء عامل الاسترداد باستخدام الاعتماديات المحقونة"""
        orchestrator = self.get('backup_orchestrator')
        return WorkerFactory.create_restore_worker(backup_to_restore, orchestrator)