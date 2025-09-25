"""
Language configuration module for multi-language support
"""
from typing import Dict
from .en import TEXTS as EN_TEXTS
from .zh import TEXTS as ZH_TEXTS


class LanguageConfig:
    """Multi-language configuration for the stock recommendation system"""
    
    def __init__(self, language: str = "en"):
        self.language = language.lower()
        self.texts = self._load_texts()
    
    def _load_texts(self) -> Dict:
        """Load text translations from resource files"""
        return ZH_TEXTS if self.language == "zh" else EN_TEXTS
    
    def get(self, key: str) -> str:
        """Get translated text by key"""
        return self.texts.get(key, key)


def get_language_config(language: str = "en") -> Dict[str, str]:
    """
    Get language configuration dictionary for the specified language.
    
    Args:
        language: Language code ('en' or 'zh')
        
    Returns:
        Dictionary with localized strings
    """
    config = LanguageConfig(language)
    return config.texts
