# ============================
# alumprocncn - Theme Model
# ============================
from PyQt5.QtCore import QSettings

APP_ORG = "alumprocncn"
APP_NAME = "Viewer"

class ThemeModel:
    """يحفظ ويحمّل تفضيل الثيم."""
    def __init__(self):
        self.settings = QSettings(APP_ORG, APP_NAME)
        self.theme = self.settings.value("theme", "dark")
        print(f"💾 [ThemeModel] Loaded theme: {self.theme}")

    def toggle(self) -> str:
        self.theme = "light" if self.theme == "dark" else "dark"
        self.settings.setValue("theme", self.theme)
        print(f"🌗 [ThemeModel] Theme switched -> {self.theme}")
        return self.theme
