from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Callable, Any


class IFileScanner(ABC):
    """تجريد لفحص وتصفية الملفات"""
    
    @abstractmethod
    def scan_files(self, paths: List[Path], exclusions: List[str]) -> List[Path]:
        """فحص المسارات وإرجاع قائمة الملفات المفلترة"""
        pass
    
    @abstractmethod
    def is_excluded(self, file_path: Path, exclusions: List[str]) -> bool:
        """فحص ما إذا كان الملف مستبعداً"""
        pass


class IBackupStrategy(ABC):
    """تجريد لاستراتيجيات النسخ الاحتياطي"""
    
    @abstractmethod
    def create_backup(self, 
                     files: List[Path], 
                     destination: Path, 
                     progress_callback: Callable[[int, str], None],
                     is_running_check: Callable[[], bool]) -> None:
        """إنشاء نسخة احتياطية"""
        pass


class IRestoreStrategy(ABC):
    """تجريد لاستراتيجيات الاسترداد"""
    
    @abstractmethod
    def restore_backup(self, 
                      source: Path, 
                      progress_callback: Callable[[int, str], None],
                      is_running_check: Callable[[], bool]) -> str:
        """استرداد نسخة احتياطية"""
        pass


class IBackupRepository(ABC):
    """تجريد لإدارة بيانات النسخ الاحتياطية"""
    
    @abstractmethod
    def get_backups_list(self) -> List[Path]:
        """الحصول على قائمة النسخ الاحتياطية"""
        pass
    
    @abstractmethod
    def get_latest_backup_manifest(self) -> Dict[str, Any]:
        """الحصول على سجل آخر نسخة احتياطية"""
        pass
    
    @abstractmethod
    def delete_backups(self, backup_paths: List[Path]) -> None:
        """حذف نسخ احتياطية محددة"""
        pass
    
    @abstractmethod
    def apply_backup_rotation(self, retention_count: int) -> int:
        """تطبيق سياسة الاحتفاظ بالنسخ"""
        pass


class IBackupOrchestrator(ABC):
    """تجريد لتنسيق عمليات النسخ الاحتياطي"""
    
    @abstractmethod
    def create_incremental_backup(self, 
                                 folders: List[Path], 
                                 backup_filepath: Path, 
                                 exclusions: List[str],
                                 progress_callback: Callable[[int, str], None],
                                 is_running_check: Callable[[], bool]) -> None:
        """تنسيق عملية النسخ التراكمي"""
        pass
    
    @abstractmethod
    def restore_from_backup(self, 
                           backup_path: Path,
                           progress_callback: Callable[[int, str], None],
                           is_running_check: Callable[[], bool]) -> str:
        """تنسيق عملية الاسترداد"""
        pass