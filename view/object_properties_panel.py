# view/object_properties_panel.py
from PyQt5.QtWidgets import (
    QDockWidget, QWidget, QVBoxLayout, QFormLayout,
    QLineEdit, QPushButton, QLabel, QHBoxLayout
)
from PyQt5.QtCore import Qt


class ObjectPropertiesPanel(QDockWidget):
    """لوحة تحكم بالكائن المحدد (تحريك على محاور X/Y/Z)."""

    def __init__(self, controller, parent=None):
        super().__init__("Object Properties", parent)
        self.setAllowedAreas(Qt.RightDockWidgetArea)
        self.controller = controller
        self.selected_actor = None

        # ✅ الواجهة الداخلية
        main_widget = QWidget()
        self.setWidget(main_widget)
        layout = QVBoxLayout(main_widget)

        # العنوان
        self.title_label = QLabel("No object selected")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setStyleSheet("font-weight: bold; color: #DDD;")
        layout.addWidget(self.title_label)

        # مدخلات الإحداثيات
        form = QFormLayout()
        self.x_input = QLineEdit("0.0")
        self.y_input = QLineEdit("0.0")
        self.z_input = QLineEdit("0.0")
        for box in [self.x_input, self.y_input, self.z_input]:
            box.setMaximumWidth(80)
            box.setStyleSheet("background-color:#333; color:#EEE; border:1px solid #555;")
        form.addRow("X:", self.x_input)
        form.addRow("Y:", self.y_input)
        form.addRow("Z:", self.z_input)
        layout.addLayout(form)

        # أزرار التحكم
        btn_layout = QHBoxLayout()
        self.move_btn = QPushButton("Move")
        self.move_btn.setStyleSheet("background-color:#5c8aff; color:white; font-weight:bold;")
        self.reset_btn = QPushButton("Reset")
        self.reset_btn.setStyleSheet("background-color:#666; color:white;")
        btn_layout.addWidget(self.move_btn)
        btn_layout.addWidget(self.reset_btn)
        layout.addLayout(btn_layout)

        layout.addStretch()

        # ربط الأزرار
        self.move_btn.clicked.connect(self._apply_move)
        self.reset_btn.clicked.connect(self._reset_inputs)

        print("[Panel] ObjectPropertiesPanel initialized ✅")

    # ---------------------------------------------------------
    # 📌 عند اختيار كائن من العارض
    # ---------------------------------------------------------
    def set_selected_actor(self, actor):
        self.selected_actor = actor
        if actor:
            self.title_label.setText("Selected Object")
        else:
            self.title_label.setText("No object selected")

    # ---------------------------------------------------------
    # 🔹 دوال التحكم
    # ---------------------------------------------------------
    def _apply_move(self):
        if self.selected_actor is None:
            print("⚠️ لم يتم تحديد كائن.")
            return
        try:
            dx = float(self.x_input.text())
            dy = float(self.y_input.text())
            dz = float(self.z_input.text())
            self.controller.move_selected(dx, dy, dz)
        except ValueError:
            print("❌ قيم غير صالحة")

    def _reset_inputs(self):
        self.x_input.setText("0.0")
        self.y_input.setText("0.0")
        self.z_input.setText("0.0")
