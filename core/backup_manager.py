
from pathlib import Path
from typing import List, Callable

from interfaces.backup_interfaces import IBackupOrchestrator
from core.file_scanner import FileScanner
from core.backup_repository import BackupRepository
from core.strategies import IncrementalBackupStrategy, SmartRestoreStrategy
from core.logging_system import ILogger, LoggerFactory
from core.error_handler import ErrorHandler, ErrorHandlerFactory


class BackupOrchestrator(IBackupOrchestrator):
    """منسق العمليات - مسؤولية واحدة: تنسيق تدفق عمليات النسخ والاسترداد"""
    
    def __init__(self, 
                 file_scanner: FileScanner = None,
                 repository: BackupRepository = None,
                 logger: ILogger = None,
                 error_handler: ErrorHandler = None):
        self.file_scanner = file_scanner or FileScanner()
        self.repository = repository or BackupRepository()
        self.logger = logger or LoggerFactory.create_default_logger()
        self.error_handler = error_handler or ErrorHandlerFactory.create_default_handler()
    
    def create_incremental_backup(self, 
                                 folders: List[Path], 
                                 backup_filepath: Path, 
                                 exclusions: List[str],
                                 progress_callback: Callable[[int, str], None],
                                 is_running_check: Callable[[], bool]) -> None:
        """تنسيق عملية النسخ التراكمي مع معالجة الأخطاء والسجلات"""
        
        self.logger.info("بدء عملية النسخ الاحتياطي التراكمي", {
            'folders_count': len(folders),
            'backup_path': str(backup_filepath),
            'exclusions_count': len(exclusions)
        })
        
        try:
            progress_callback(0, "جارٍ البحث عن النسخة السابقة...")
            old_manifest = self.repository.get_latest_backup_manifest()
            
            progress_callback(5, "جارٍ حصر الملفات الجديدة والمعدلة...")
            all_files = self.file_scanner.scan_files(folders, exclusions)
            
            self.logger.info(f"تم العثور على {len(all_files)} ملف للمعالجة")
            
            # إنشاء استراتيجية النسخ التراكمي
            backup_strategy = IncrementalBackupStrategy(old_manifest)
            
            # تنفيذ النسخ مع معالجة الأخطاء
            safe_backup = self.error_handler.create_safe_operation(
                backup_strategy.create_backup,
                "إنشاء النسخة الاحتياطية"
            )
            
            safe_backup(all_files, backup_filepath, progress_callback, is_running_check)
            
            self.logger.info("اكتملت عملية النسخ الاحتياطي بنجاح", {
                'backup_path': str(backup_filepath)
            })
            
        except Exception as e:
            context = {
                'folders': [str(f) for f in folders],
                'backup_filepath': str(backup_filepath),
                'exclusions': exclusions
            }
            
            if not self.error_handler.handle_exception(e, context, "النسخ الاحتياطي التراكمي"):
                self.logger.critical("فشل في النسخ الاحتياطي ولم يتم الاسترداد")
                raise
    
    def restore_from_backup(self, 
                           backup_path: Path,
                           progress_callback: Callable[[int, str], None],
                           is_running_check: Callable[[], bool]) -> str:
        """تنسيق عملية الاسترداد مع معالجة الأخطاء والسجلات"""
        
        self.logger.info("بدء عملية الاسترداد", {
            'backup_path': str(backup_path)
        })
        
        try:
            restore_strategy = SmartRestoreStrategy()
            
            # تنفيذ الاسترداد مع معالجة الأخطاء
            safe_restore = self.error_handler.create_safe_operation(
                restore_strategy.restore_backup,
                "استرداد النسخة الاحتياطية"
            )
            
            result = safe_restore(backup_path, progress_callback, is_running_check)
            
            self.logger.info("اكتملت عملية الاسترداد بنجاح", {
                'backup_path': str(backup_path)
            })
            
            return result
            
        except Exception as e:
            context = {
                'backup_path': str(backup_path)
            }
            
            if not self.error_handler.handle_exception(e, context, "استرداد النسخة الاحتياطية"):
                self.logger.critical("فشل في الاسترداد ولم يتم الاسترداد")
                raise


# للتوافق مع الكود الموجود - سيتم إزالته لاحقاً
class BackupManager(BackupOrchestrator):
    """فئة انتقالية للتوافق مع الكود الموجود"""
    
    def __init__(self):
        super().__init__()
    
    def get_backups_list(self) -> List[Path]:
        return self.repository.get_backups_list()
    
    def get_latest_backup_manifest(self) -> dict:
        return self.repository.get_latest_backup_manifest()
    
    def delete_backups(self, backup_paths: List[Path]) -> int:
        deleted_count = 0
        for path in backup_paths:
            try:
                if path and path.exists():
                    path.unlink()
                    deleted_count += 1
            except OSError:
                pass
        return deleted_count
    
    def apply_backup_rotation(self, retention_count: int) -> int:
        return self.repository.apply_backup_rotation(retention_count)
