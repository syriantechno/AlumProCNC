# main_window.py
from pathlib import Path
import ctypes

from PyQt5.QtCore import Qt, QSize, QTimer, QPoint
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QToolBar, QAction
)

from view.vtk_qt_viewer import VTKQtViewer
from controller.main_controller import MainController
from frontend.window.profiles_library_window import ProfilesLibraryWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("AlumProMainWindow")
        self.setWindowTitle("AlumProCNC — VTK/Qt (Stable)")
        self.resize(1600, 900)

        # ===== Viewer + Controller =====
        self.viewer = VTKQtViewer(self)
        self.setCentralWidget(self.viewer)
        self.controller = MainController(self.viewer)

        # ===== Style (Dark) =====
        self._apply_unified_style()

        # ===== Toolbar =====
        self._setup_toolbar()

        # default language (can wire to your LanguageManager later)
        self.current_lang = "en"

        print("✅ [MainWindow] Ready — Viewer + Controller initialized")

        # Keep ref for the library window (single instance)
        self._profiles_win = None

    # -------------------------------------------------
    # Toolbar
    # -------------------------------------------------
    def _setup_toolbar(self):
        tb = QToolBar("MainToolbar", self)
        tb.setMovable(False)
        tb.setIconSize(QSize(18, 18))
        self.addToolBar(Qt.TopToolBarArea, tb)

        # 📚 Profiles Library (text icon as requested)
        act_profiles = QAction("📚 Profiles", self)
        act_profiles.setToolTip("Open Profiles Library")
        act_profiles.triggered.connect(self._open_profiles_library)
        tb.addAction(act_profiles)

        # (Optional) quick action to reload style (useful during tweaks)
        act_reload_style = QAction("🎨 Reload Style", self)
        act_reload_style.setToolTip("Reload alum_style.qss")
        act_reload_style.triggered.connect(self._apply_unified_style)
        tb.addAction(act_reload_style)

    # -------------------------------------------------
    # Style Loader
    # -------------------------------------------------
    def _apply_unified_style(self):
        """
        Load dark Fusion-style QSS. If missing, enforce a safe dark fallback.
        """
        try:
            qss_path = Path("frontend/style/alum_style.qss")
            if qss_path.exists():
                self.setStyleSheet(qss_path.read_text(encoding="utf-8"))
                print("🎨 [Style] Applied AlumProCNC Dark Theme (QSS)")
            else:
                self.setStyleSheet("""
                    QMainWindow, QWidget { background-color: #1E1E1E; color: #E0E0E0; }
                    QToolBar { background: #1B1B1B; border: none; }
                    QPushButton { background:#2B2B2B; color:#E0E0E0; border-radius:6px; padding:6px 12px; }
                    QPushButton:hover { background:#00BCD4; color:#111; }
                """)
                print("⚠️ [Style] QSS not found — applied dark fallback.")
        except Exception as e:
            print(f"❌ [Style ERROR] {e}")

    # -------------------------------------------------
    # Open Profiles Library (independent window)
    # -------------------------------------------------
    # main_window.py  (مقتطف دالة واحدة)
    from PyQt5.QtCore import Qt, QTimer, QPoint
    from PyQt5.QtWidgets import QApplication
    import ctypes  # اختياري

    def _open_profiles_library(self):
        try:
            # أنشئ/أعد استخدام نافذة واحدة فقط
            if getattr(self, "_profiles_win", None) is None:
                from frontend.window.profiles_library_window import ProfilesLibraryWindow
                self._profiles_win = ProfilesLibraryWindow(parent=None)

                # نافذة Tool مستقلة، تبقى فوق
                self._profiles_win.setWindowFlags(
                    Qt.Tool | Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint
                )
                self._profiles_win.setWindowModality(Qt.NonModal)
                self._profiles_win.setAttribute(Qt.WA_DeleteOnClose)
                self._profiles_win.setMinimumSize(900, 600)

            # أظهرها بقوة
            self._profiles_win.showNormal()
            self._profiles_win.show()
            self._profiles_win.raise_()
            self._profiles_win.activateWindow()
            self._profiles_win.setFocus(Qt.ActiveWindowFocusReason)

            # (اختياري) إجبار foreground في ويندوز
            try:
                hwnd = int(self._profiles_win.winId())
                ctypes.windll.user32.SetForegroundWindow(hwnd)
            except Exception:
                pass

            # تمركز في منتصف الشاشة (وليس نسبة للـMain)
            screen = QApplication.primaryScreen().availableGeometry()
            g = self._profiles_win.frameGeometry()
            g.moveCenter(screen.center())
            self._profiles_win.move(g.topLeft())

            print("📚 [ProfilesLibrary] Window shown and focused ✅")

        except Exception as e:
            print(f"❌ [ProfilesLibrary] Failed to open: {e}")

    def _center_child_on_self(self):
        """Center the library window relative to the MainWindow geometry."""
        if not self._profiles_win:
            return
        # If size not computed yet, use sizeHint
        w = self._profiles_win.width() or self._profiles_win.sizeHint().width()
        h = self._profiles_win.height() or self._profiles_win.sizeHint().height()

        center = self.geometry().center()
        x = center.x() - (w // 2)
        y = center.y() - (h // 2)

        # Ensure on-screen (in case of multi-monitor)
        if x < 0: x = 50
        if y < 0: y = 50

        self._profiles_win.move(QPoint(x, y))

    # -------------------------------------------------
    # Clean exit (optional)
    # -------------------------------------------------
    def closeEvent(self, event):
        try:
            if hasattr(self.viewer, "renWin") and self.viewer.renWin:
                self.viewer.renWin.Finalize()
                print("🧹 [VTK] Finalized render window.")
        except Exception as e:
            print(f"⚠️ [VTK] Finalize on exit failed: {e}")
        event.accept()


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
