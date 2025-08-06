import sys
import os
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui.main_window_new import AlHirzApp

# إعدادات Linux للعرض
if sys.platform.startswith('linux'):
    try:
        import shutil
        if shutil.which("Xorg") or shutil.which("Xwayland"):
            os.environ["QT_QPA_PLATFORM"] = "xcb"
        else:
            print("تحذير: نظامك قد لا يدعم xcb، سيتم محاولة استخدام Wayland.")
    except Exception as e:
        print(f"حدث خطأ أثناء تحديد بيئة العرض: {e}")

def main():
    """نقطة الدخول الرئيسية للتطبيق."""
    app = QApplication(sys.argv)

    # تفعيل دعم اليمين لليسار للتطبيق بأكمله
    app.setLayoutDirection(Qt.RightToLeft)

    window = AlHirzApp()
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
