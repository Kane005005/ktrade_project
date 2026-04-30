import requests
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)

class CurrencyConverter:
    """
    Convertisseur de devises utilisant une API publique
    """
    
    API_URL = "https://api.exchangerate-api.com/v4/latest/"
    CACHE_TIMEOUT = 3600  # 1 heure
    
    # Mapping des devises
    CURRENCY_SYMBOLS = {
        'USD': '$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CNY': '¥',
        'XOF': 'CFA',
        'XAF': 'FCFA',
    }
    
    @classmethod
    def get_exchange_rate(cls, from_currency, to_currency):
        """
        Récupère le taux de change entre deux devises
        """
        if from_currency == to_currency:
            return 1.0
        
        # Clé de cache
        cache_key = f"exchange_rate_{from_currency}_{to_currency}"
        rate = cache.get(cache_key)
        
        if rate is None:
            try:
                # Appel API
                response = requests.get(f"{cls.API_URL}{from_currency}", timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    rate = data['rates'].get(to_currency)
                    
                    if rate:
                        # Mettre en cache
                        cache.set(cache_key, rate, cls.CACHE_TIMEOUT)
                else:
                    logger.error(f"Erreur API taux de change: {response.status_code}")
                    rate = cls.get_fallback_rate(from_currency, to_currency)
                    
            except Exception as e:
                logger.error(f"Erreur lors de la récupération du taux de change: {e}")
                rate = cls.get_fallback_rate(from_currency, to_currency)
        
        return rate
    
    @classmethod
    def get_fallback_rate(cls, from_currency, to_currency):
        """
        Taux de change de secours (statiques)
        """
        fallback_rates = {
            ('USD', 'EUR'): 0.92,
            ('EUR', 'USD'): 1.09,
            ('USD', 'XOF'): 605.0,
            ('XOF', 'USD'): 0.00165,
            ('EUR', 'XOF'): 655.96,
            ('XOF', 'EUR'): 0.00152,
            ('USD', 'GBP'): 0.79,
            ('GBP', 'USD'): 1.27,
        }
        
        return fallback_rates.get((from_currency, to_currency), 1.0)
    
    @classmethod
    def convert(cls, amount, from_currency, to_currency):
        """
        Convertit un montant d'une devise à une autre
        """
        rate = cls.get_exchange_rate(from_currency, to_currency)
        converted = amount * rate
        
        return {
            'amount': round(amount, 2),
            'from_currency': from_currency,
            'to_currency': to_currency,
            'converted': round(converted, 2),
            'rate': round(rate, 4),
            'symbol': cls.CURRENCY_SYMBOLS.get(to_currency, to_currency)
        }
    
    @classmethod
    def get_popular_currencies(cls):
        """
        Retourne une liste des devises populaires
        """
        return [
            {'code': 'USD', 'name': 'Dollar US', 'symbol': '$'},
            {'code': 'EUR', 'name': 'Euro', 'symbol': '€'},
            {'code': 'XOF', 'name': 'Franc CFA', 'symbol': 'CFA'},
            {'code': 'GBP', 'name': 'Livre Sterling', 'symbol': '£'},
            {'code': 'CNY', 'name': 'Yuan Chinois', 'symbol': '¥'},
        ]