"""Exchange Factory Pattern"""

from typing import Dict, Any, Optional
from src.exchanges.base import BaseExchange


class ExchangeFactory:
    """Factory for creating exchange instances"""

    _exchanges: Dict[str, Any] = {}

    @staticmethod
    def register(exchange_name: str, exchange_class):
        """Register an exchange class"""
        ExchangeFactory._exchanges[exchange_name.lower()] = exchange_class

    @staticmethod
    def create(
        exchange_name: str,
        api_key: str,
        api_secret: str,
        **kwargs
    ) -> BaseExchange:
        """
        Create and return exchange instance
        
        Args:
            exchange_name: Name of exchange (binance, coinbase, kraken)
            api_key: Exchange API key
            api_secret: Exchange API secret
            **kwargs: Additional parameters
            
        Returns:
            BaseExchange instance
            
        Raises:
            ValueError: If exchange not registered
        """
        exchange_class = ExchangeFactory._exchanges.get(exchange_name.lower())
        if not exchange_class:
            raise ValueError(f"Exchange '{exchange_name}' not registered")
        
        return exchange_class(api_key, api_secret, **kwargs)

    @staticmethod
    def get_available_exchanges() -> list:
        """Get list of available exchange names"""
        return list(ExchangeFactory._exchanges.keys())
