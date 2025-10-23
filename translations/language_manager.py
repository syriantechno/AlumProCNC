# language_manager.py
from translations.lang_en import translations_en
from translations.lang_ar import translations_ar

class LanguageManager:
    def __init__(self):
        self.current_lang = "en"
        self.translations = translations_en

    def switch(self):
        """Toggle between English / Arabic"""
        if self.current_lang == "en":
            self.current_lang = "ar"
            self.translations = translations_ar
        else:
            self.current_lang = "en"
            self.translations = translations_en
        print(f"[LANG] switched to {self.current_lang.upper()}")
        return self.translations

    def get_translations(self):
        return self.translations
