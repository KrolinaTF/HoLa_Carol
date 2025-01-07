from deep_translator import GoogleTranslator
from typing import Union, Dict, List

class TranslationService:
    def __init__(self):
        self.translator_es_en = GoogleTranslator(source='es', target='en')
        self.translator_en_es = GoogleTranslator(source='en', target='es')

    def to_english(self, text: str) -> str:
        """Traduce texto de español a inglés"""
        try:
            return self.translator_es_en.translate(text)
        except Exception as e:
            logger.error(f"Error en traducción a inglés: {str(e)}")
            return text

    def to_spanish(self, text: Union[str, Dict, List]) -> Union[str, Dict, List]:
        """Traduce texto de inglés a español"""
        try:
            if isinstance(text, str):
                return self.translator_en_es.translate(text)
            elif isinstance(text, dict):
                return {k: self.to_spanish(v) for k, v in text.items()}
            elif isinstance(text, list):
                return [self.to_spanish(item) for item in text]
            return text
        except Exception as e:
            logger.error(f"Error en traducción a español: {str(e)}")
            return text