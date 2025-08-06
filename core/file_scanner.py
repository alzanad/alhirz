import fnmatch
from pathlib import Path
from typing import List

from interfaces.backup_interfaces import IFileScanner
from utils.config import HOME_DIR


class FileScanner(IFileScanner):
    """مسؤولية واحدة: فحص وتصفية الملفات حسب قواعد الاستبعاد"""
    
    def scan_files(self, paths: List[Path], exclusions: List[str]) -> List[Path]:
        """فحص المسارات وإرجاع قائمة الملفات المفلترة"""
        files = []
        
        for folder_path in paths:
            if not folder_path.is_dir():
                continue
                
            for file in folder_path.rglob('*'):
                if not file.is_file():
                    continue
                    
                if not self.is_excluded(file, exclusions):
                    files.append(file)
        
        return files
    
    def is_excluded(self, file_path: Path, exclusions: List[str]) -> bool:
        """فحص ما إذا كان الملف مستبعداً حسب قواعد الاستبعاد"""
        try:
            relative_path = file_path.relative_to(HOME_DIR)
        except ValueError:
            return True
        
        # فحص تطابق أي جزء من المسار (للمجلدات مثل __pycache__)
        if any(fnmatch.fnmatch(part, pattern) 
               for pattern in exclusions 
               for part in relative_path.parts):
            return True
        
        # فحص تطابق اسم الملف نفسه (للملفات مثل *.tmp)
        if any(fnmatch.fnmatch(relative_path.name, pattern) 
               for pattern in exclusions):
            return True
        
        return False