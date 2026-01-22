"""Base Exchange Class"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class BaseExchange(ABC):
    """Abstract base class for exchange implementations"""

    def __init__(self, api_key: str, api_secret: str, **kwargs):
        """
        Initialize exchange connection
        
        Args:
            api_key: Exchange API key
            api_secret: Exchange API secret
            **kwargs: Additional exchange-specific parameters
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.exchange_name = None

    @abstractmethod
    async def get_balance(self) -> Dict[str, Any]:
        """Get account balance"""
        pass

    @abstractmethod
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get current ticker price"""
        pass

    @abstractmethod
    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Get order book"""
        pass

    @abstractmethod
    async def get_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> List[List[Any]]:
        """Get OHLCV candle data"""
        pass

    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        amount: float,
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Place a trade order"""
        pass

    @abstractmethod
    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel an order"""
        pass

    @abstractmethod
    async def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status"""
        pass

    @abstractmethod
    async def close(self):
        """Close exchange connection"""
        pass
