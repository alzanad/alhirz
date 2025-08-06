import json
import zipfile
from pathlib import Path
from typing import List, Callable, Dict, Any

from interfaces.backup_interfaces import IBackupStrategy, IRestoreStrategy
from utils.config import HOME_DIR, MANIFEST_FILENAME


class IncrementalBackupStrategy(IBackupStrategy):
    """استراتيجية النسخ التراكمي - مسؤولية واحدة: إنشاء نسخ تراكمية"""
    
    def __init__(self, old_manifest: Dict[str, Any]):
        self.old_manifest = old_manifest
    
    def create_backup(self, 
                     files: List[Path], 
                     destination: Path, 
                     progress_callback: Callable[[int, str], None],
                     is_running_check: Callable[[], bool]) -> None:
        """إنشاء نسخة احتياطية تراكمية"""
        
        # تحديد الملفات التي تحتاج نسخ
        files_to_backup = self._filter_files_for_backup(files)
        new_manifest = self._create_manifest(files)
        
        total_files = len(files_to_backup)
        
        if total_files == 0:
            progress_callback(100, "لا توجد ملفات جديدة أو معدّلة لنسخها.")
            # إنشاء ملف بسجل محدث إذا كان هناك تغيير في السجل
            if self.old_manifest.keys() != new_manifest.keys():
                self._create_manifest_only_backup(destination, new_manifest)
            return
        
        # إنشاء النسخة الاحتياطية
        with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for i, file in enumerate(files_to_backup):
                if not is_running_check():
                    raise InterruptedError("تم إلغاء العملية.")
                
                progress = 10 + int((i / total_files) * 85)
                progress_callback(progress, f"يتم ضغط: {file.name[:30]}...")
                
                zipf.write(file, file.relative_to(HOME_DIR))
            
            progress_callback(98, "جارٍ كتابة سجل النسخة...")
            zipf.writestr(MANIFEST_FILENAME, json.dumps(new_manifest, indent=2))
        
        progress_callback(100, "اكتمل الضغط.")
    
    def _filter_files_for_backup(self, files: List[Path]) -> List[Path]:
        """تصفية الملفات التي تحتاج نسخ احتياطي"""
        files_to_backup = []
        
        for file in files:
            relative_path_str = str(file.relative_to(HOME_DIR))
            current_mtime = file.stat().st_mtime
            
            # فحص إذا كان الملف جديد أو معدل
            is_newly_included = (relative_path_str not in self.old_manifest and 
                               relative_path_str in self.old_manifest.get('_excluded_files', []))
            
            if (relative_path_str not in self.old_manifest or 
                current_mtime > self.old_manifest.get(relative_path_str, 0) or 
                is_newly_included):
                files_to_backup.append(file)
        
        return files_to_backup
    
    def _create_manifest(self, files: List[Path]) -> Dict[str, Any]:
        """إنشاء سجل النسخة الجديد"""
        manifest = {}
        
        for file in files:
            relative_path_str = str(file.relative_to(HOME_DIR))
            current_mtime = file.stat().st_mtime
            manifest[relative_path_str] = current_mtime
        
        return manifest
    
    def _create_manifest_only_backup(self, destination: Path, manifest: Dict[str, Any]) -> None:
        """إنشاء نسخة تحتوي على السجل فقط"""
        with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.writestr(MANIFEST_FILENAME, json.dumps(manifest, indent=2))


class SmartRestoreStrategy(IRestoreStrategy):
    """استراتيجية الاسترداد الذكي - مسؤولية واحدة: استرداد الملفات بذكاء"""
    
    def restore_backup(self, 
                      source: Path, 
                      progress_callback: Callable[[int, str], None],
                      is_running_check: Callable[[], bool]) -> str:
        """استرداد النسخة الاحتياطية بذكاء (تخطي الموجود)"""
        
        with zipfile.ZipFile(source, 'r') as zipf:
            all_files_info = [info for info in zipf.infolist() 
                            if info.filename != MANIFEST_FILENAME]
            total_files = len(all_files_info)
            restored_count = 0
            skipped_count = 0
            
            for i, member in enumerate(all_files_info):
                if not is_running_check():
                    raise InterruptedError("تم إلغاء العملية.")
                
                target_path = HOME_DIR / Path(member.filename)
                progress = (i + 1) * 100 // total_files
                progress_callback(progress, f"معالجة: {target_path.name[:40]}...")
                
                if target_path.exists():
                    skipped_count += 1
                    continue
                
                target_path.parent.mkdir(parents=True, exist_ok=True)
                zipf.extract(member, HOME_DIR)
                restored_count += 1
        
        return (f"اكتمل الاسترداد الذكي بنجاح!\n\n"
                f"✓ تم استرداد {restored_count} ملفاً جديداً.\n"
                f"↷ تم تخطي {skipped_count} ملفاً لوجودها مسبقاً.")