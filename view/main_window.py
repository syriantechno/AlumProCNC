from PyQt5.QtWidgets import QMainWindow, QAction, QToolBar, QFrame, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt
from view.vtk_qt_viewer import VTKQtViewer
from controller.main_controller import MainController
from view.object_properties_panel import ObjectPropertiesPanel
# الثيم الجديد (مجلدان منفصلان كما أرسلنا سابقًا)
from frontend.theme.theme_model import ThemeModel
from frontend.theme.theme_styles import fusion_stylesheet


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("AlumProMainWindow")
        self.setWindowTitle("AlumProCNC — VTK/Qt (Stable)")
        self.resize(1600, 900)

        # 🔹 تحميل الثيم من الإعدادات
        self._theme_model = ThemeModel()
        self.setStyleSheet(fusion_stylesheet(self._theme_model.theme))

        # 🔹 تغليف العارض داخل حاوية لتطبيق خلفية أنيقة
        center = QWidget(self)
        center.setObjectName("ViewerContainer")
        center_layout = QVBoxLayout(center)
        center_layout.setContentsMargins(8, 8, 8, 8)
        center_layout.setSpacing(0)

        # 🧭 العارض ثلاثي الأبعاد (VTK)
        self.viewer = VTKQtViewer(self)
        center_layout.addWidget(self.viewer)
        self.setCentralWidget(center)

        # 🔧 الكنترولر والـ Dock كما هما
        self.controller = MainController(self.viewer)
        self.properties_panel = ObjectPropertiesPanel(self.controller, self)
        self.addDockWidget(Qt.RightDockWidgetArea, self.properties_panel)

        # ربط اختيار الكائنات
        self.viewer.on_object_selected = self.properties_panel.set_selected_actor

        # 🎨 إعداد الشريط العلوي
        self._setup_toolbar()
        self._add_theme_toggle_to_toolbar()
        self._add_top_separator()

    # ------------------------------------------------------------------ #
    def _setup_toolbar(self):
        """شريط الأدوات الأساسي (كما هو)."""
        tb = self.addToolBar("Main")
        tb.setMovable(False)
        tb.setFloatable(False)

        act_box = QAction("Create Box", self)
        act_box.triggered.connect(self.controller.create_box)
        tb.addAction(act_box)

        act_import = QAction("Import DXF", self)
        act_import.triggered.connect(self.controller.import_dxf)
        tb.addAction(act_import)

    # ------------------------------------------------------------------ #
    def _add_theme_toggle_to_toolbar(self):
        """زر تبديل الثيم 🌙 ↔ ☀️."""
        toolbars = self.findChildren(QToolBar)
        if toolbars:
            tb = toolbars[0]
        else:
            tb = QToolBar("Main", self)
            self.addToolBar(tb)

        self.action_toggle_theme = QAction("Theme", self)
        self.action_toggle_theme.setToolTip("Toggle Light/Dark Theme")
        self.action_toggle_theme.triggered.connect(self._toggle_theme)
        tb.addSeparator()
        tb.addAction(self.action_toggle_theme)

    def _add_top_separator(self):
        """فاصل رفيع أسفل الشريط لإحساس Fusion."""
        sep = QFrame(self)
        sep.setObjectName("TopSeparator")
        sep.setFrameShape(QFrame.HLine)
        sep.setFixedHeight(1)

        sep_bar = QToolBar(self)
        sep_bar.setMovable(False)
        sep_bar.setFloatable(False)
        sep_bar.setFixedHeight(1)
        sep_bar.addWidget(sep)
        self.addToolBarBreak()
        self.addToolBar(sep_bar)

    # ------------------------------------------------------------------ #
    def _toggle_theme(self):
        """تبديل الثيم وتطبيق الستايل فوراً."""
        new_theme = self._theme_model.toggle()
        self.setStyleSheet(fusion_stylesheet(new_theme))
        print(f"🌗 [UI] Theme toggled to: {new_theme}")
