# -*- coding: utf-8 -*-
"""
الحِرز: أداة النسخ الاحتياطي الذكي
==============================================

"الحِرز" هي أداة بايثون مستقلة، تعمل عبر مختلف أنظمة التشغيل (ويندوز، ماك، لينكس)
لإجراء نسخ احتياطي انتقائي واسترداد ذكي للمجلدات الهامة في دليل المستخدم.

"""

import os
import sys
import shutil
import zipfile
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

# --- قسم الألوان والواجهة ---

class Colors:
    """فئة لتخزين أكواد الألوان لطباعة نصية منسقة."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def enable_windows_colors():
    """تفعيل دعم الألوان في طرفية ويندوز التقليدية."""
    if os.name == 'nt':
        os.system('')

def print_color(text: str, color: str):
    """طباعة نص بلون محدد."""
    print(f"{color}{text}{Colors.ENDC}")

def clear_screen():
    """مسح شاشة الطرفية."""
    os.system('cls' if os.name == 'nt' else 'clear')

# --- إعدادات الأداة والمسارات المحدثة ---

TOOL_NAME = "الحِرز"
ROOT_CONFIG_DIR_NAME = ".AlZanad"
TOOL_SUBDIR_NAME = "alhirz"
BACKUP_SUBDIR = "backups"

HOME_DIR = Path.home()
# المسار الجديد والمحدد: HOME/.AlZanad/alhirz/backups
BACKUP_DIR = HOME_DIR / ROOT_CONFIG_DIR_NAME / TOOL_SUBDIR_NAME / BACKUP_SUBDIR

def setup_environment():
    """
    التأكد من وجود مجلد النسخ الاحتياطي بالبنية الجديدة.
    تقوم بإنشائه إذا لم يكن موجودًا.
    """
    try:
        # إنشاء المسار الكامل بما في ذلك المجلدات الوسيطة
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    except OSError as e:
        print_color(f"[خطأ] تعذّر إنشاء مجلدات الإعدادات في المسار: {BACKUP_DIR}", Colors.RED)
        print_color(f"السبب: {e}", Colors.RED)
        sys.exit(1)

# --- الوظائف الأساسية: النسخ والاسترداد ---

def get_default_source_folders() -> List[Path]:
    """
    الحصول على قائمة بالمجلدات الافتراضية الموجودة فعلاً في دليل المستخدم.
    """
    default_folders = ["Documents", "Downloads", "Desktop", "Pictures", "Music", "Videos"]
    existing_folders = [HOME_DIR / folder for folder in default_folders if (HOME_DIR / folder).is_dir()]
    return existing_folders

def create_backup():
    """
    إدارة عملية إنشاء نسخة احتياطية جديدة كاملة، مع خيار الإقصاء والإضافة.
    """
    clear_screen()
    print_color(f"--- إنشاء نسخة احتياطية جديدة باستخدام {TOOL_NAME} ---", Colors.HEADER)

    source_folders = get_default_source_folders()
    if not source_folders:
        print_color("\nلم يتم العثور على أي من المجلدات الافتراضية المعروفة.", Colors.YELLOW)
    else:
        print_color("\n[معلومات] تم العثور على المجلدات الافتراضية التالية:", Colors.BLUE)
        for i, folder in enumerate(source_folders):
            print(f"  {Colors.CYAN}{i+1}{Colors.ENDC}. {folder.name}")

        exclude_input = input(f"\n{Colors.CYAN}هل ترغب في إقصاء أي من هذه المجلدات؟\n(أدخل الأرقام مفصولة بمسافة، مثال: 1 4، أو اضغط Enter لتضمين الكل): {Colors.ENDC}")
        if exclude_input.strip():
            try:
                indices_to_exclude = {int(x.strip()) - 1 for x in exclude_input.split()}

                if any(i < 0 or i >= len(source_folders) for i in indices_to_exclude):
                    raise ValueError("أحد الأرقام المدخلة خارج النطاق الصحيح.")

                excluded_folders = [source_folders[i].name for i in sorted(list(indices_to_exclude), reverse=True)]
                source_folders = [folder for i, folder in enumerate(source_folders) if i not in indices_to_exclude]

                print_color(f"[معلومات] تم إقصاء المجلدات: {', '.join(excluded_folders)}", Colors.YELLOW)

            except ValueError as e:
                print_color(f"[خطأ] إدخال غير صالح. لم يتم إقصاء أي مجلد. السبب: {e}", Colors.RED)

    while True:
        try:
            choice = input(f"\n{Colors.CYAN}هل ترغب في إضافة مجلدات أخرى؟ (1: نعم / 2: لا): {Colors.ENDC}")
            if choice not in ['1', '2']:
                raise ValueError("الرجاء إدخال 1 أو 2 فقط.")
            break
        except ValueError as e:
            print_color(f"[خطأ] {e}", Colors.RED)

    if choice == '1':
        print_color("\nأدخل مسارات المجلدات الإضافية. اضغط Enter بمفرده لإنهاء الإضافة:", Colors.CYAN)
        while True:
            path_str = input("> ")
            if not path_str:
                break

            additional_path = Path(path_str).expanduser().resolve()
            if additional_path.is_dir():
                if additional_path not in source_folders:
                    source_folders.append(additional_path)
                    print_color(f"[نجاح] تمت إضافة المجلد: {additional_path}", Colors.GREEN)
                else:
                    print_color("[تنبيه] هذا المجلد موجود بالفعل في القائمة.", Colors.YELLOW)
            else:
                print_color("[خطأ] المسار المدخل ليس مجلداً صالحاً أو غير موجود.", Colors.RED)

    if not source_folders:
        print_color("\n[خطأ] لم يتم تحديد أي مجلدات للنسخ. تم إلغاء العملية.", Colors.RED)
        return

    print_color("\n[معلومات] بدء عملية النسخ الاحتياطي...", Colors.BLUE)
    final_folder_names = [p.name if p.parent == HOME_DIR else str(p) for p in source_folders]
    print_color(f"[معلومات] المجلدات المستهدفة: {', '.join(final_folder_names)}", Colors.BLUE)

    timestamp = datetime.now().strftime('%Y-%m-%d_%H%M%S')
    backup_filename = f"نسخة_احتياطية_{timestamp}.zip"
    backup_filepath = BACKUP_DIR / backup_filename

    try:
        with zipfile.ZipFile(backup_filepath, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for folder_path in source_folders:
                print_color(f"[معلومات] جارٍ نسخ مجلد '{folder_path.name}'...", Colors.YELLOW)
                for file in folder_path.rglob('*'):
                    zipf.write(file, file.relative_to(HOME_DIR))
                print_color(f"[نجاح] تم نسخ مجلد '{folder_path.name}' بنجاح.", Colors.GREEN)

        print_color("\n[معلومات] جارٍ ضغط الأرشيف...", Colors.BLUE)
        final_size_mb = backup_filepath.stat().st_size / (1024 * 1024)

        print_color("\n" + "="*50, Colors.GREEN)
        print_color(f"       اكتملت عملية النسخ الاحتياطي بنجاح!", Colors.BOLD + Colors.GREEN)
        print_color("="*50, Colors.GREEN)
        print_color(f"تم إنشاء النسخة الاحتياطية في المسار:\n{backup_filepath}", Colors.CYAN)
        print_color(f"الحجم النهائي للملف: {final_size_mb:.2f} ميجابايت", Colors.CYAN)

    except (OSError, zipfile.BadZipFile, PermissionError) as e:
        print_color(f"\n[خطأ فادح] فشلت عملية النسخ الاحتياطي!", Colors.RED)
        print_color(f"السبب: {e}", Colors.RED)
        if backup_filepath.exists():
            backup_filepath.unlink() # حذف الملف غير المكتمل
    except Exception as e:
        print_color(f"\n[خطأ غير متوقع] حدث خطأ: {e}", Colors.RED)


def restore_from_backup():
    """
    إدارة عملية استرداد البيانات من نسخة احتياطية موجودة.
    """
    clear_screen()
    print_color(f"--- استرداد بيانات من نسخة احتياطية ---", Colors.HEADER)

    if not BACKUP_DIR.exists():
        print_color("\n[خطأ] مجلد النسخ الاحتياطي غير موجود. هل قمت بإنشاء نسخة من قبل؟", Colors.RED)
        return

    available_backups = sorted(
        [f for f in BACKUP_DIR.glob('*.zip') if f.is_file()],
        key=os.path.getmtime,
        reverse=True
    )

    if not available_backups:
        print_color("\n[خطأ] لا توجد أي نسخ احتياطية متاحة للاسترداد.", Colors.RED)
        return

    print_color("\nالنسخ الاحتياطية المتاحة:", Colors.BLUE)
    for i, backup_file in enumerate(available_backups):
        file_date = datetime.fromtimestamp(backup_file.stat().st_mtime).strftime('%Y-%m-%d %H:%M')
        print(f"  {Colors.CYAN}{i+1}{Colors.ENDC}. {backup_file.name}  ({Colors.YELLOW}{file_date}{Colors.ENDC})")

    while True:
        try:
            choice_str = input(f"\n{Colors.CYAN}الرجاء اختيار رقم النسخة التي تود استردادها: {Colors.ENDC}")
            choice = int(choice_str) - 1
            if not 0 <= choice < len(available_backups):
                raise ValueError("الرقم المدخل خارج النطاق.")
            break
        except ValueError:
            print_color("[خطأ] إدخال غير صالح. الرجاء إدخال رقم من القائمة.", Colors.RED)

    selected_backup = available_backups[choice]

    print_color(f"\n[معلومات] تم اختيار النسخة: {selected_backup.name}", Colors.BLUE)
    print_color("[معلومات] ستبدأ عملية الاسترداد الذكي (دمج). لن يتم استبدال أي ملف موجود.", Colors.BLUE)

    try:
        with zipfile.ZipFile(selected_backup, 'r') as zipf:
            all_files = zipf.infolist()
            total_files = len(all_files)
            skipped_count, restored_count = 0, 0

            print_color("\n[معلومات] جارٍ استرداد الملفات...", Colors.YELLOW)

            for i, member in enumerate(all_files):
                target_path = HOME_DIR / Path(member.filename)
                progress = (i + 1) / total_files
                progress_bar = f"[{'#' * int(progress * 20):<20}] {int(progress * 100)}%"
                print(f"\r{Colors.YELLOW}يتم الآن معالجة: {member.filename[:40].ljust(40)} {progress_bar}{Colors.ENDC}", end="")

                if target_path.exists():
                    skipped_count += 1
                    continue

                if member.is_dir():
                    target_path.mkdir(parents=True, exist_ok=True)
                else:
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    zipf.extract(member, HOME_DIR)
                    restored_count += 1

        print("\n")
        print_color("\n" + "="*50, Colors.GREEN)
        print_color("     اكتملت عملية الاسترداد الذكي بنجاح!", Colors.BOLD + Colors.GREEN)
        print_color("="*50, Colors.GREEN)
        print_color(f"تم استرداد {restored_count} ملفاً جديداً.", Colors.CYAN)
        print_color(f"تم تخطي {skipped_count} ملفاً لأنها موجودة مسبقاً.", Colors.CYAN)

    except (zipfile.BadZipFile, OSError, PermissionError) as e:
        print_color(f"\n[خطأ فادح] فشلت عملية الاسترداد!", Colors.RED)
        print_color(f"السبب: {e}", Colors.RED)
    except Exception as e:
        print_color(f"\n[خطأ غير متوقع] حدث خطأ: {e}", Colors.RED)

# --- القائمة الرئيسية وحلقة البرنامج ---

def main():
    """
    الوظيفة الرئيسية التي تدير حلقة البرنامج والقائمة التفاعلية.
    """
    enable_windows_colors()
    setup_environment()

    while True:
        clear_screen()
        print_color("=" * 40, Colors.HEADER)
        print_color(f"       أهلاً بك في أداة {TOOL_NAME} للحفظ الأمين", Colors.BOLD + Colors.HEADER)
        print_color("=" * 40, Colors.HEADER)
        print_color("\nالرجاء اختيار الإجراء المطلوب:", Colors.BLUE)
        print(f"  {Colors.CYAN}1.{Colors.ENDC} إنشاء نسخة احتياطية جديدة")
        print(f"  {Colors.CYAN}2.{Colors.ENDC} استرداد بيانات من نسخة احتياطية")
        print(f"  {Colors.CYAN}3.{Colors.ENDC} الخروج")

        choice = input(f"\n{Colors.CYAN}ادخل رقم اختيارك: {Colors.ENDC}")

        if choice == '1':
            create_backup()
        elif choice == '2':
            restore_from_backup()
        elif choice == '3':
            print_color(f"\nمع السلامة، بياناتك في حِرزٍ أمين.", Colors.GREEN)
            break
        else:
            print_color("\n[خطأ] اختيار غير صالح. الرجاء المحاولة مرة أخرى.", Colors.RED)

        input(f"\n{Colors.YELLOW}اضغط على زر الإدخال (Enter) للعودة إلى القائمة الرئيسية...{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_color("\n\n[تنبيه] تم إيقاف البرنامج من قبل المستخدم. إلى اللقاء.", Colors.YELLOW)
        sys.exit(0)
