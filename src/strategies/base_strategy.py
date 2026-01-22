"""Base Strategy Class"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class BaseStrategy(ABC):
    """Abstract base class for trading strategies"""

    def __init__(self, name: str, risk_percentage: float = 0.02):
        """
        Initialize strategy
        
        Args:
            name: Strategy name
            risk_percentage: Risk percentage per trade (default 2%)
        """
        self.name = name
        self.risk_percentage = risk_percentage

    @abstractmethod
    async def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze market data and generate trading signal
        
        Args:
            market_data: Current market data
            
        Returns:
            Trading signal with action and parameters
        """
        pass

    @abstractmethod
    async def validate_risk(self, position_size: float, entry_price: float, stop_loss: float) -> bool:
        """
        Validate risk parameters before placing order
        
        Args:
            position_size: Size of position
            entry_price: Entry price
            stop_loss: Stop loss price
            
        Returns:
            True if risk is acceptable
        """
        pass

    def calculate_position_size(self, account_balance: float, risk_amount: float) -> float:
        """Calculate position size based on risk"""
        return risk_amount / account_balance
