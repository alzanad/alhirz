# -*- coding: utf-8 -*-
"""
المقدم الرئيسي - Presenter في MVP Pattern
مسؤولية واحدة: تنسيق التفاعل بين View و Model
"""

from datetime import datetime
from pathlib import Path
from typing import List, Optional

from interfaces.ui_interfaces import IMainView, IMainPresenter, IBackupModel
from core.factories import ServiceContainer
from core.logging_system import ILogger, LoggerFactory
from utils.config import BACKUP_DIR


class MainPresenter(IMainPresenter):
    """المقدم الرئيسي - ينسق بين View و Model"""
    
    def __init__(self, 
                 view: IMainView,
                 model: IBackupModel,
                 service_container: ServiceContainer = None,
                 logger: ILogger = None):
        self.view = view
        self.model = model
        self.service_container = service_container or ServiceContainer()
        self.logger = logger or LoggerFactory.create_default_logger()
        self.current_worker = None
    
    def start_backup(self) -> None:
        """بدء عملية النسخ الاحتياطي"""
        try:
            # التحقق من المجلدات المحددة
            selected_folders = self.view.get_selected_folders()
            if not selected_folders:
                self.view.show_message(
                    "لا توجد مجلدات", 
                    "الرجاء اختيار مجلد واحد على الأقل.",
                    "warning"
                )
                return
            
            # إعداد معاملات النسخ
            exclusions = self.view.get_exclusions()
            timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
            backup_filepath = BACKUP_DIR / f"نسخة_{timestamp}.zip"
            
            # تعطيل عناصر التحكم
            self.view.toggle_controls(False, 'backup')
            self.view.update_progress(0, "جارٍ التحضير...", 'backup')
            
            # إنشاء وتشغيل العامل
            self.current_worker = self.service_container.create_backup_worker(
                selected_folders, backup_filepath, exclusions
            )
            
            # ربط الإشارات
            self.current_worker.progress_update.connect(
                lambda p, s: self.view.update_progress(p, s, 'backup')
            )
            self.current_worker.finished.connect(
                lambda msg: self._on_backup_finished(msg)
            )
            
            self.current_worker.start()
            self.logger.info("بدء عملية النسخ الاحتياطي")
            
        except Exception as e:
            self.logger.error(f"فشل في بدء النسخ الاحتياطي: {e}")
            self.view.show_message(
                "خطأ في النسخ", 
                f"حدث خطأ أثناء بدء النسخ الاحتياطي:\n{e}",
                "error"
            )
            self.view.toggle_controls(True, 'backup')
    
    def start_restore(self) -> None:
        """بدء عملية الاسترداد"""
        try:
            # التحقق من النسخة المحددة
            selected_backup = self.view.get_selected_backup()
            if not selected_backup:
                self.view.show_message(
                    "لم يتم الاختيار", 
                    "الرجاء اختيار نسخة احتياطية.",
                    "warning"
                )
                return
            
            # تأكيد الاسترداد
            if not self.view.show_confirmation(
                "تأكيد الاسترداد",
                f"هل أنت متأكد؟ سيتم دمج الملفات ولن يتم استبدال أي ملف موجود."
            ):
                return
            
            # تعطيل عناصر التحكم
            self.view.toggle_controls(False, 'restore')
            
            # إنشاء وتشغيل العامل
            self.current_worker = self.service_container.create_restore_worker(selected_backup)
            
            # ربط الإشارات
            self.current_worker.progress_update.connect(
                lambda p, s: self.view.update_progress(p, s, 'restore')
            )
            self.current_worker.finished.connect(
                lambda msg: self._on_restore_finished(msg)
            )
            
            self.current_worker.start()
            self.logger.info(f"بدء عملية الاسترداد من: {selected_backup}")
            
        except Exception as e:
            self.logger.error(f"فشل في بدء الاسترداد: {e}")
            self.view.show_message(
                "خطأ في الاسترداد", 
                f"حدث خطأ أثناء بدء الاسترداد:\n{e}",
                "error"
            )
            self.view.toggle_controls(True, 'restore')
    
    def cancel_operation(self) -> None:
        """إلغاء العملية الجارية"""
        if self.current_worker and self.current_worker.isRunning():
            self.current_worker.stop()
            self.logger.info("تم طلب إلغاء العملية")
    
    def delete_backups(self) -> None:
        """حذف النسخ المحددة"""
        try:
            selected_backups = self.view.get_selected_backups_for_deletion()
            if not selected_backups:
                self.view.show_message(
                    "لم يتم الاختيار", 
                    "الرجاء تحديد نسخة لحذفها.",
                    "warning"
                )
                return
            
            count = len(selected_backups)
            if not self.view.show_confirmation(
                "تأكيد الحذف",
                f"هل أنت متأكد من حذف {count} من النسخ نهائياً؟"
            ):
                return
            
            deleted_count = self.model.delete_backups(selected_backups)
            
            if deleted_count > 0:
                self.view.show_message(
                    "اكتمل الحذف", 
                    f"تم حذف {deleted_count} من النسخ بنجاح.",
                    "info"
                )
                self.view.refresh_backups_list()
                self.logger.info(f"تم حذف {deleted_count} نسخة احتياطية")
            else:
                self.view.show_message(
                    "فشل الحذف", 
                    "لم يتم حذف أي نسخة.",
                    "warning"
                )
                
        except Exception as e:
            self.logger.error(f"فشل في حذف النسخ: {e}")
            self.view.show_message(
                "خطأ في الحذف", 
                f"حدث خطأ أثناء حذف النسخ:\n{e}",
                "error"
            )
    
    def add_custom_folder(self, folder_path: str) -> None:
        """إضافة مجلد مخصص"""
        try:
            if not folder_path:
                return
            
            path_obj = Path(folder_path)
            
            # التحقق من صحة المسار
            if not self.model.validate_folder_path(path_obj):
                self.view.show_message(
                    "مسار غير صحيح", 
                    "المسار المحدد غير موجود أو ليس مجلداً.",
                    "warning"
                )
                return
            
            # التحقق من التكرار
            existing_folders = self.view.get_selected_folders()
            if self.model.is_folder_already_added(path_obj, existing_folders):
                self.view.show_message(
                    "مجلد مكرر", 
                    "هذا المجلد موجود بالفعل.",
                    "warning"
                )
                return
            
            self.logger.info(f"تم إضافة مجلد مخصص: {folder_path}")
            
        except Exception as e:
            self.logger.error(f"فشل في إضافة المجلد: {e}")
            self.view.show_message(
                "خطأ في الإضافة", 
                f"حدث خطأ أثناء إضافة المجلد:\n{e}",
                "error"
            )
    
    def remove_custom_folder(self) -> None:
        """إزالة مجلد مخصص"""
        # هذه العملية تتم في View مباشرة
        # لأنها تتعلق بالتفاعل مع عناصر الواجهة
        pass
    
    def add_exclusion(self, exclusion_pattern: str) -> None:
        """إضافة استثناء"""
        try:
            if not exclusion_pattern.strip():
                return
            
            if self.model.add_exclusion(exclusion_pattern):
                self.logger.info(f"تم إضافة استثناء: {exclusion_pattern}")
            else:
                self.view.show_message(
                    "استثناء موجود", 
                    "هذا الاستثناء م��جود بالفعل.",
                    "warning"
                )
                
        except Exception as e:
            self.logger.error(f"فشل في إضافة الاستثناء: {e}")
            self.view.show_message(
                "خطأ في الإضافة", 
                f"حدث خطأ أثناء إضافة الاستثناء:\n{e}",
                "error"
            )
    
    def remove_exclusion(self) -> None:
        """إزالة استثناء"""
        # هذه العملية تتم في View مباشرة
        # لأنها تتعلق بالتفاعل مع عناصر الواجهة
        pass
    
    def refresh_backups(self) -> None:
        """تحديث قائمة النسخ"""
        try:
            self.view.refresh_backups_list()
            self.logger.info("تم تحديث قائمة النسخ الاحتياطية")
        except Exception as e:
            self.logger.error(f"فشل في تحديث قائمة النسخ: {e}")
    
    def _on_backup_finished(self, message: str) -> None:
        """معالجة انتهاء عملية النسخ"""
        self.view.toggle_controls(True, 'backup')
        self.current_worker = None
        
        if "اكتمل" in message:
            self.view.show_message("نجاح العملية", message, "info")
            
            # تطبيق دوران النسخ
            try:
                retention_count = self.view.get_retention_count()
                deleted_count = self.model.apply_backup_rotation(retention_count)
                if deleted_count > 0:
                    self.logger.info(f"تم تنظيف {deleted_count} من النسخ القديمة")
            except Exception as e:
                self.logger.error(f"فشل في تطبيق دوران النسخ: {e}")
            
            self.view.refresh_backups_list()
            
        elif "إلغاء" in message:
            self.view.show_message("تم الإلغاء", message, "warning")
        else:
            self.view.show_message("فشل العملية", message, "error")
    
    def _on_restore_finished(self, message: str) -> None:
        """معالجة انتهاء عملية الاسترداد"""
        self.view.toggle_controls(True, 'restore')
        self.current_worker = None
        
        if "اكتمل" in message:
            self.view.show_message("نجاح العملية", message, "info")
        elif "إلغاء" in message:
            self.view.show_message("تم الإلغاء", message, "warning")
        else:
            self.view.show_message("فشل العملية", message, "error")