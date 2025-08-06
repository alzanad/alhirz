
# -*- coding: utf-8 -*-
from pathlib import Path

TOOL_NAME = "الحِرز"
ROOT_CONFIG_DIR_NAME = ".AlZanad"
TOOL_SUBDIR_NAME = "alhirz"
BACKUP_SUBDIR = "backups"
MANIFEST_FILENAME = "manifest.json"
SETTINGS_FILENAME = "settings.json"

HOME_DIR = Path.home()
APP_DIR = HOME_DIR / ROOT_CONFIG_DIR_NAME / TOOL_SUBDIR_NAME
BACKUP_DIR = APP_DIR / BACKUP_SUBDIR

# إعدادات افتراضية
DEFAULT_FOLDERS = ["Documents", "Downloads", "Desktop", "Pictures", "Music", "Videos"]
DEFAULT_BACKUP_RETENTION = 5 # عدد النسخ الافتراضي للاحتفاظ بها
DEFAULT_EXCLUSIONS = [
    "__pycache__", "*.tmp", "*.bak", "*.log", "node_modules",
    "*.cache", "*.swp", "*.swo", "*.pyc", "*.pyo", "*.pyd",
    ".git", ".svn", ".hg", ".bzr", "CVS",
    "Thumbs.db", ".DS_Store", "desktop.ini",
    "*.iso", "*.img", "*.vmdk", "*.vdi",
    ".vscode", ".idea", "*.sublime-*",
    "build", "dist", "target", "bin", "obj",
    ".npm", ".yarn", ".gradle", ".m2"
]
