import requests
import json
from django.core.cache import cache
import logging
from googletrans import Translator
import hashlib

logger = logging.getLogger(__name__)

class MessageTranslator:
    """
    Traducteur de messages utilisant Google Translate
    """
    
    CACHE_TIMEOUT = 86400  # 24 heures
    
    # Langues supportées
    SUPPORTED_LANGUAGES = {
        'fr': 'Français',
        'en': 'English',
        'es': 'Español',
        'de': 'Deutsch',
        'it': 'Italiano',
        'pt': 'Português',
        'ar': 'العربية',
        'zh-cn': '中文',
        'ja': '日本語',
        'ru': 'Русский',
        'nl': 'Nederlands',
        'tr': 'Türkçe',
    }
    
    def __init__(self):
        self.translator = Translator()
    
    def translate(self, text, dest_language='fr', src_language='auto'):
        """
        Traduit un texte vers la langue de destination
        """
        if not text:
            return None
        
        # Clé de cache basée sur le texte et la langue
        cache_key = self._generate_cache_key(text, dest_language, src_language)
        translated = cache.get(cache_key)
        
        if translated is None:
            try:
                # Traduction
                result = self.translator.translate(text, dest=dest_language, src=src_language)
                translated = result.text
                
                # Mettre en cache
                cache.set(cache_key, translated, self.CACHE_TIMEOUT)
                
            except Exception as e:
                logger.error(f"Erreur de traduction: {e}")
                translated = text
        
        return translated
    
    def detect_language(self, text):
        """
        Détecte la langue d'un texte
        """
        try:
            detection = self.translator.detect(text)
            return {
                'lang': detection.lang,
                'confidence': detection.confidence
            }
        except Exception as e:
            logger.error(f"Erreur de détection de langue: {e}")
            return {'lang': 'unknown', 'confidence': 0}
    
    def _generate_cache_key(self, text, dest_language, src_language):
        """
        Génère une clé de cache unique
        """
        key_string = f"{text}_{dest_language}_{src_language}"
        return f"translation_{hashlib.md5(key_string.encode()).hexdigest()}"
    
    @classmethod
    def get_language_name(cls, code):
        """
        Retourne le nom d'une langue à partir de son code
        """
        return cls.SUPPORTED_LANGUAGES.get(code, code)