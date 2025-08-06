import os
import json
import zipfile
from pathlib import Path
from typing import List, Dict, Any

from interfaces.backup_interfaces import IBackupRepository
from utils.config import BACKUP_DIR, MANIFEST_FILENAME


class BackupRepository(IBackupRepository):
    """مسؤولية واحدة: إدارة الوصول لبيانات النسخ الاحتياطية"""
    
    def get_backups_list(self) -> List[Path]:
        """الحصول على قائمة النسخ الاحتياطية مرتبة من الأحدث للأقدم"""
        if not BACKUP_DIR.exists():
            return []
        
        return sorted(
            [f for f in BACKUP_DIR.glob('*.zip') if f.is_file()],
            key=os.path.getmtime,
            reverse=True
        )
    
    def get_latest_backup_manifest(self) -> Dict[str, Any]:
        """الحصول على سجل آخر نسخة احتياطية"""
        backups = self.get_backups_list()
        if not backups:
            return {}
        
        latest_backup = backups[0]
        return self._read_manifest_from_backup(latest_backup)
    
    def delete_backups(self, backup_paths: List[Path]) -> None:
        """حذف نسخ احتياطية محددة"""
        for path in backup_paths:
            try:
                if path.exists():
                    path.unlink()
            except OSError:
                pass
    
    def apply_backup_rotation(self, retention_count: int) -> int:
        """تطبيق سياسة الاحتفاظ بالنسخ وحذف الأقدم"""
        backups = self.get_backups_list()
        
        if len(backups) <= retention_count:
            return 0
        
        to_delete = backups[retention_count:]
        self.delete_backups(to_delete)
        return len(to_delete)
    
    def _read_manifest_from_backup(self, backup_path: Path) -> Dict[str, Any]:
        """قراءة سجل النسخة من ملف النسخة الاحتياطية"""
        try:
            with zipfile.ZipFile(backup_path, 'r') as zipf:
                if MANIFEST_FILENAME in zipf.namelist():
                    with zipf.open(MANIFEST_FILENAME) as manifest_file:
                        return json.load(manifest_file)
        except Exception:
            pass
        
        return {}