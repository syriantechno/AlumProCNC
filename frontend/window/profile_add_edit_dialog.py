# frontend/window/profile_add_edit_dialog.py
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QFileDialog, QMessageBox, QHBoxLayout
)
from pathlib import Path

class ProfileAddEditDialog(QDialog):
    def __init__(self, db, parent=None, profile=None, translations=None):
        super().__init__(parent)
        self.db = db
        self.profile = profile
        self.tr = translations or {}
        self.setWindowTitle(self.tr.get("add_profile", "Add Profile"))
        self.resize(400, 250)

        self.name = QLineEdit()
        self.company = QLineEdit()
        self.width = QLineEdit()
        self.height = QLineEdit()
        self.sku = QLineEdit()
        self.dxf_path = QLineEdit()
        self.image_path = QLineEdit()

        self.btn_browse = QPushButton(self.tr.get("browse", "Browse DXF"))
        self.btn_save = QPushButton(self.tr.get("save", "Save"))
        self.btn_cancel = QPushButton(self.tr.get("cancel", "Cancel"))

        self.btn_browse.clicked.connect(self.browse_file)
        self.btn_save.clicked.connect(self.save)
        self.btn_cancel.clicked.connect(self.close)

        form = QFormLayout()
        form.addRow("Name:", self.name)
        form.addRow("Company:", self.company)
        form.addRow("Width:", self.width)
        form.addRow("Height:", self.height)
        form.addRow("SKU:", self.sku)
        form.addRow(self.btn_browse, self.dxf_path)

        layout = QVBoxLayout()
        layout.addLayout(form)

        btns = QHBoxLayout()
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_cancel)
        layout.addLayout(btns)
        self.setLayout(layout)

        if profile:
            self.load_profile(profile)

    def load_profile(self, profile):
        pid, name, company, w, h, sku, dxf, img = profile
        self.name.setText(name)
        self.company.setText(company)
        self.width.setText(str(w))
        self.height.setText(str(h))
        self.sku.setText(sku)
        self.dxf_path.setText(dxf)
        self.image_path.setText(img)

    def browse_file(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select DXF File", "", "DXF Files (*.dxf)")
        if path:
            self.dxf_path.setText(path)

    def save(self):
        if not self.name.text().strip():
            QMessageBox.warning(self, "Error", "Name cannot be empty")
            return

        self.db.add_profile(
            self.name.text(), self.company.text(),
            float(self.width.text() or 0),
            float(self.height.text() or 0),
            self.sku.text(), self.dxf_path.text(), ""
        )
        self.accept()
