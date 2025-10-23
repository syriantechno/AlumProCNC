from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QScrollArea, QWidget, QGridLayout, QGraphicsDropShadowEffect
)
from PyQt5.QtGui import QPixmap, QColor, QPalette, QFont
from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve, QSize


class ProfilesLibraryWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setObjectName("ProfilesLibraryWindow")
        self.resize(950, 550)
        self.setAutoFillBackground(True)

        # 🖤 خلفية داكنة بتدرج ناعم
        palette = self.palette()
        gradient_color = QColor("#1E1E1E")
        palette.setColor(self.backgroundRole(), gradient_color)
        self.setPalette(palette)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ===== Title Bar =====
        title_bar = QFrame()
        title_bar.setFixedHeight(40)
        title_bar.setObjectName("TitleBar")
        title_bar.setStyleSheet("""
            QFrame#TitleBar {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1B1B1B, stop:1 #202020
                );
                border-top-left-radius: 12px;
                border-top-right-radius: 12px;
            }
        """)

        title_layout = QHBoxLayout(title_bar)
        title_layout.setContentsMargins(12, 0, 12, 0)
        title_layout.setSpacing(8)

        title_lbl = QLabel("Profiles Library")
        title_lbl.setFont(QFont("Roboto Medium", 11))
        title_lbl.setStyleSheet("color: #E0E0E0;")

        # أزرار تحكم
        btn_min = QPushButton("–")
        btn_max = QPushButton("□")
        btn_close = QPushButton("✕")
        for b in (btn_min, btn_max, btn_close):
            b.setFixedSize(26, 22)
            b.setFlat(True)
            b.setCursor(Qt.PointingHandCursor)
            b.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    color: #AAA;
                    border: none;
                    font-size: 12px;
                }
                QPushButton:hover {
                    color: white;
                    background-color: #2A2A2A;
                    border-radius: 4px;
                }
            """)
        btn_close.clicked.connect(self.close)
        btn_min.clicked.connect(self.showMinimized)
        btn_max.clicked.connect(self.showNormal)

        title_layout.addWidget(title_lbl)
        title_layout.addStretch()
        title_layout.addWidget(btn_min)
        title_layout.addWidget(btn_max)
        title_layout.addWidget(btn_close)
        main_layout.addWidget(title_bar)

        # ===== زرار الأدوات =====
        btn_bar = QFrame()
        btn_bar.setStyleSheet("background-color: #1E1E1E;")
        btn_layout = QHBoxLayout(btn_bar)
        btn_layout.setContentsMargins(12, 8, 12, 8)
        btn_layout.setSpacing(10)

        self.btn_add = self.make_colored_button("＋ Add", "#2E7D32")     # أخضر
        self.btn_edit = self.make_colored_button("✎ Edit", "#EF6C00")   # برتقالي
        self.btn_delete = self.make_colored_button("🗑 Delete", "#C62828")  # أحمر

        btn_layout.addWidget(self.btn_add)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_delete)
        btn_layout.addStretch()
        main_layout.addWidget(btn_bar)

        # ===== منطقة البطاقات =====
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAutoFillBackground(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea, QScrollArea QWidget {
                background-color: qlineargradient(
                    spread:pad, x1:0, y1:0, x2:0, y2:1,
                    stop:0 #1C1C1C, stop:1 #202020
                );
                border: none;
            }
        """)

        self.scroll_widget = QWidget()
        self.scroll_widget.setAutoFillBackground(True)
        self.scroll_widget.setStyleSheet("background-color: transparent;")
        self.grid_layout = QGridLayout(self.scroll_widget)
        self.grid_layout.setSpacing(15)
        self.scroll_area.setWidget(self.scroll_widget)
        main_layout.addWidget(self.scroll_area)

        # تحميل بيانات تجريبية
        self.load_profiles([
            {"name": "60x60 BN", "company": "Alumil", "size": "60×60 mm", "sku": "DGF4415JH52", "image": ""},
            {"name": "40x40", "company": "Technal", "size": "40×40 mm", "sku": "T12345", "image": ""},
            {"name": "45x90", "company": "Reynaers", "size": "45×90 mm", "sku": "R9099", "image": ""},
        ])

        # تأثير Fade عند الفتح
        self.fade_in_animation()

    # -----------------------------------------------------
    def make_colored_button(self, text, color):
        btn = QPushButton(text)
        btn.setFixedHeight(28)
        btn.setCursor(Qt.PointingHandCursor)
        btn.setFont(QFont("Roboto", 9))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border-radius: 6px;
                padding: 4px 12px;
                border: none;
            }}
            QPushButton:hover {{
                background-color: {self._brighten(color, 20)};
            }}
        """)
        return btn

    def _brighten(self, color_hex, percent):
        c = QColor(color_hex)
        h, s, v, a = c.getHsv()
        v = min(255, v + int(255 * (percent / 100)))
        c.setHsv(h, s, v, a)
        return c.name()

    # -----------------------------------------------------
    def load_profiles(self, profiles):
        for i in reversed(range(self.grid_layout.count())):
            widget = self.grid_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        for idx, profile in enumerate(profiles):
            card = self.create_card(profile)
            row, col = divmod(idx, 4)
            self.grid_layout.addWidget(card, row, col)

    # -----------------------------------------------------
    def create_card(self, data):
        card = QFrame()
        card.setObjectName("ProfileCard")
        card.setFixedSize(190, 210)

        # ظل ناعم حول البطاقة
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 3)
        shadow.setColor(QColor(0, 0, 0, 180))
        card.setGraphicsEffect(shadow)

        card.setStyleSheet("""
            QFrame#ProfileCard {
                background-color: #252525;
                border-radius: 10px;
                border: 1px solid #2A2A2A;
                transition: all 0.2s ease;
            }
            QFrame#ProfileCard:hover {
                background-color: #2E2E2E;
                border: 1px solid #00BCD4;
                margin-top: -2px;
            }
        """)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)

        img = QLabel()
        img.setAlignment(Qt.AlignCenter)
        img.setFixedSize(150, 90)
        if data.get("image"):
            pix = QPixmap(data["image"]).scaled(150, 90, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            img.setPixmap(pix)
        else:
            img.setText("No Image")
            img.setStyleSheet("color: #777; border: 1px dashed #555; font-size: 11px;")

        name_lbl = QLabel(data.get("name", ""))
        name_lbl.setStyleSheet("color: #00BCD4; font-weight: bold; font-size: 11px;")

        comp_lbl = QLabel(data.get("company", ""))
        comp_lbl.setStyleSheet("color: #C8C8C8; font-size: 10px;")

        size_lbl = QLabel(data.get("size", ""))
        size_lbl.setStyleSheet("color: #C8C8C8; font-size: 10px;")

        sku_lbl = QLabel("SKU: " + data.get("sku", ""))
        sku_lbl.setStyleSheet("color: #888; font-size: 9px;")

        open_btn = QPushButton("Open")
        open_btn.setFixedHeight(24)
        open_btn.setCursor(Qt.PointingHandCursor)
        open_btn.setStyleSheet("""
            QPushButton {
                background-color: #00BCD4;
                color: white;
                border-radius: 6px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #26D7E8;
            }
        """)

        layout.addWidget(img)
        layout.addWidget(name_lbl)
        layout.addWidget(comp_lbl)
        layout.addWidget(size_lbl)
        layout.addWidget(sku_lbl)
        layout.addStretch()
        layout.addWidget(open_btn, alignment=Qt.AlignCenter)

        return card

    # -----------------------------------------------------
    def fade_in_animation(self):
        """حركة دخول ناعمة عند فتح النافذة"""
        self.setWindowOpacity(0.0)
        anim = QPropertyAnimation(self, b"windowOpacity")
        anim.setDuration(400)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.setEasingCurve(QEasingCurve.InOutQuad)
        anim.start(QPropertyAnimation.DeleteWhenStopped)
