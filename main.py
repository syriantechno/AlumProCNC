# main.py  (مقتطف مهم فقط)
from pathlib import Path
from PyQt5.QtWidgets import QApplication
# ... بقية الاستيرادات

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)

    # ✅ حمّل ستايل داكن موحّد
    qss_path = Path("frontend/style/fusion_dark.qss")
    if qss_path.exists():
        app.setStyleSheet(qss_path.read_text(encoding="utf-8"))
        print("🎨 [Style] Dark Fusion applied successfully")
    else:
        print("⚠️ [Style] QSS not found — using fallback dark")
        app.setStyleSheet("""
            QMainWindow, QWidget { background:#1e1e1e; color:#e0e0e0; }
            QToolBar { background:#202020; border:none; }
        """)

    # شغّل نافذتك الرئيسية كالمعتاد
    from view.main_window import MainWindow  # حسب مسارك
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
