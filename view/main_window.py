from PyQt5.QtWidgets import QMainWindow, QApplication, QAction, QToolBar
from PyQt5.QtCore import Qt, QSize
from pathlib import Path

from view.vtk_qt_viewer import VTKQtViewer
from controller.main_controller import MainController
from frontend.window.profiles_library_window import ProfilesLibraryWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("AlumProCNC — PyVista Edition")
        self.resize(1600, 900)

        # 🟢 Viewer
        self.viewer = VTKQtViewer(self)
        self.setCentralWidget(self.viewer)

        # 🟢 Controller
        self.controller = MainController(self.viewer)

        # 🟢 Toolbar
        self._setup_toolbar()

        # 🟢 Apply the unified dark theme
        self._apply_alum_style()

        print("✅ [MainWindow] Ready — Viewer + Controller initialized")

    # -------------------------------------------------
    # Toolbar setup
    # -------------------------------------------------
    def _setup_toolbar(self):
        toolbar = QToolBar("MainToolbar", self)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        # 📂 Profiles Library
        act_profiles = QAction("Profiles Library", self)
        act_profiles.triggered.connect(self._open_profiles_library)
        toolbar.addAction(act_profiles)

        # 🌗 Toggle Theme
        act_theme = QAction("Toggle Theme", self)
        act_theme.triggered.connect(self._apply_alum_style)
        toolbar.addAction(act_theme)

    # -------------------------------------------------
    # Open profiles library
    # -------------------------------------------------
    def _open_profiles_library(self):
        try:
            self.library = ProfilesLibraryWindow(self)
            self.library.setModal(False)
            self.library.show()
            self.library.raise_()  # 🔹 تأكد إنها فوق كل النوافذ
            self.library.activateWindow()  # 🔹 ركّز عليها
            self.library.move(
                self.geometry().center().x() - self.library.width() // 2,
                self.geometry().center().y() - self.library.height() // 2
            )  # 🔹 افتحها بالمنتصف
            print("📚 [ProfilesLibrary] Window shown and focused ✅")
        except Exception as e:
            print(f"❌ [ProfilesLibrary] Failed to open: {e}")

    # -------------------------------------------------
    # Apply the alum dark style (Fusion-style)
    # -------------------------------------------------
    def _apply_alum_style(self):
        try:
            qss_path = Path("frontend/style/alum_style.qss")
            if qss_path.exists():
                qss = qss_path.read_text(encoding="utf-8")
                self.setStyleSheet(qss)
                print("🎨 [Style] Applied AlumProCNC Dark Theme")
            else:
                print("⚠️ [Style] QSS not found, using fallback color")
                self.setStyleSheet("QWidget { background-color: #181818; color: #E0E0E0; }")
        except Exception as e:
            print(f"❌ [Style ERROR] {e}")


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
