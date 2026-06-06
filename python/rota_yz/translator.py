from __future__ import annotations

from deep_translator import GoogleTranslator

from rota_yz.text_utils import normalize_text


class TranslationService:
    def translate(self, text: str, target: str) -> str:
        cleaned = normalize_text(text)
        if not cleaned:
            return cleaned

        try:
            translated = GoogleTranslator(source="auto", target=target).translate(cleaned)
        except Exception:
            return cleaned

        return normalize_text(translated or cleaned)

    def translate_to_english(self, text: str) -> str:
        return self.translate(text, "en")

    def translate_to_turkish(self, text: str) -> str:
        return self.translate(text, "tr")
