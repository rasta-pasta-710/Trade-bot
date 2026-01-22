"""Base Strategy Class"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
import numpy as np


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

    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> List[float]:
        """Calculate Simple Moving Average"""
        if len(prices) < period:
            return []
        
        sma = []
        for i in range(period - 1, len(prices)):
            avg = sum(prices[i - period + 1:i + 1]) / period
            sma.append(avg)
        return sma

    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> List[float]:
        """Calculate Exponential Moving Average"""
        if len(prices) < period:
            return []
        
        multiplier = 2 / (period + 1)
        ema = [sum(prices[:period]) / period]
        
        for i in range(period, len(prices)):
            ema.append(prices[i] * multiplier + ema[-1] * (1 - multiplier))
        
        return ema

    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> List[float]:
        """Calculate Relative Strength Index"""
        if len(prices) < period + 1:
            return []
        
        deltas = [prices[i] - prices[i - 1] for i in range(1, len(prices))]
        gains = [d if d > 0 else 0 for d in deltas]
        losses = [abs(d) if d < 0 else 0 for d in deltas]
        
        rsi = []
        avg_gain = sum(gains[:period]) / period
        avg_loss = sum(losses[:period]) / period
        
        for i in range(period, len(gains)):
            avg_gain = (avg_gain * (period - 1) + gains[i]) / period
            avg_loss = (avg_loss * (period - 1) + losses[i]) / period
            
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi_value = 100 - (100 / (1 + rs)) if rs != 0 else 50
            rsi.append(rsi_value)
        
        return rsi

    @staticmethod
    def calculate_macd(prices: List[float], fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, List[float]]:
        """Calculate MACD (Moving Average Convergence Divergence)"""
        ema_fast = BaseStrategy.calculate_ema(prices, fast)
        ema_slow = BaseStrategy.calculate_ema(prices, slow)
        
        # MACD line
        macd_line = [ema_fast[i] - ema_slow[i] for i in range(len(ema_slow))]
        
        # Signal line
        signal_line = BaseStrategy.calculate_ema(macd_line, signal)
        
        # Histogram
        histogram = [macd_line[i] - signal_line[i] if i < len(signal_line) else 0 
                    for i in range(len(macd_line))]
        
        return {
            "macd": macd_line,
            "signal": signal_line,
            "histogram": histogram
        }

    @staticmethod
    def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: int = 2) -> Dict[str, List[float]]:
        """Calculate Bollinger Bands"""
        if len(prices) < period:
            return {"upper": [], "middle": [], "lower": []}
        
        upper = []
        middle = []
        lower = []
        
        for i in range(period - 1, len(prices)):
            window = prices[i - period + 1:i + 1]
            avg = sum(window) / period
            variance = sum((x - avg) ** 2 for x in window) / period
            std = variance ** 0.5
            
            middle.append(avg)
            upper.append(avg + std_dev * std)
            lower.append(avg - std_dev * std)
        
        return {"upper": upper, "middle": middle, "lower": lower}

    @staticmethod
    def calculate_volatility(prices: List[float], period: int = 20) -> List[float]:
        """Calculate historical volatility"""
        if len(prices) < period + 1:
            return []
        
        volatility = []
        for i in range(period, len(prices)):
            window = prices[i - period:i + 1]
            returns = [np.log(window[j] / window[j - 1]) for j in range(1, len(window))]
            std = np.std(returns)
            volatility.append(std)
        
        return volatility
