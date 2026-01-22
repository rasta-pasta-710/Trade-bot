"""SMA Crossover Strategy"""

from typing import Dict, Any, List
from src.strategies.base_strategy import BaseStrategy


class SMAcrossoverStrategy(BaseStrategy):
    """Simple Moving Average Crossover Strategy"""

    def __init__(self, fast_period: int = 10, slow_period: int = 20, risk_percentage: float = 0.02):
        """Initialize SMA crossover strategy"""
        super().__init__("SMA Crossover", risk_percentage)
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.last_signal = None

    async def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze using SMA crossover
        
        Args:
            market_data: Market data with OHLCV candles
            
        Returns:
            Trading signal
        """
        if "closes" not in market_data or len(market_data["closes"]) < self.slow_period:
            return {"action": "hold", "reason": "Insufficient data"}

        closes = market_data["closes"]
        
        # Calculate SMAs
        sma_fast = self.calculate_sma(closes, self.fast_period)
        sma_slow = self.calculate_sma(closes, self.slow_period)

        if not sma_fast or not sma_slow:
            return {"action": "hold", "reason": "Cannot calculate SMAs"}

        # Get current values
        current_fast = sma_fast[-1]
        current_slow = sma_slow[-1]
        prev_fast = sma_fast[-2] if len(sma_fast) > 1 else current_fast
        prev_slow = sma_slow[-2] if len(sma_slow) > 1 else current_slow

        # Check crossover
        signal = None
        if prev_fast <= prev_slow and current_fast > current_slow:
            signal = "buy"
        elif prev_fast >= prev_slow and current_fast < current_slow:
            signal = "sell"

        return {
            "action": signal or "hold",
            "sma_fast": current_fast,
            "sma_slow": current_slow,
            "price": closes[-1]
        }

    async def validate_risk(self, position_size: float, entry_price: float, stop_loss: float) -> bool:
        """Validate risk parameters"""
        if entry_price == 0 or stop_loss == 0:
            return False
        if entry_price == stop_loss:
            return False
        return True


class RSIStrategy(BaseStrategy):
    """RSI Overbought/Oversold Strategy"""

    def __init__(self, rsi_period: int = 14, overbought: int = 70, oversold: int = 30, risk_percentage: float = 0.02):
        """Initialize RSI strategy"""
        super().__init__("RSI", risk_percentage)
        self.rsi_period = rsi_period
        self.overbought = overbought
        self.oversold = oversold

    async def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze using RSI"""
        if "closes" not in market_data or len(market_data["closes"]) < self.rsi_period + 1:
            return {"action": "hold", "reason": "Insufficient data"}

        closes = market_data["closes"]
        rsi_values = self.calculate_rsi(closes, self.rsi_period)

        if not rsi_values:
            return {"action": "hold", "reason": "Cannot calculate RSI"}

        current_rsi = rsi_values[-1]

        signal = None
        if current_rsi < self.oversold:
            signal = "buy"
        elif current_rsi > self.overbought:
            signal = "sell"

        return {
            "action": signal or "hold",
            "rsi": current_rsi,
            "price": closes[-1],
            "overbought": self.overbought,
            "oversold": self.oversold
        }

    async def validate_risk(self, position_size: float, entry_price: float, stop_loss: float) -> bool:
        """Validate risk parameters"""
        return entry_price != 0 and stop_loss != 0 and entry_price != stop_loss


class MACDStrategy(BaseStrategy):
    """MACD Crossover Strategy"""

    def __init__(self, fast: int = 12, slow: int = 26, signal: int = 9, risk_percentage: float = 0.02):
        """Initialize MACD strategy"""
        super().__init__("MACD", risk_percentage)
        self.fast = fast
        self.slow = slow
        self.signal = signal

    async def analyze(self, market_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze using MACD"""
        if "closes" not in market_data or len(market_data["closes"]) < self.slow + self.signal:
            return {"action": "hold", "reason": "Insufficient data"}

        closes = market_data["closes"]
        macd_data = self.calculate_macd(closes, self.fast, self.slow, self.signal)

        if not macd_data["signal"] or not macd_data["histogram"]:
            return {"action": "hold", "reason": "Cannot calculate MACD"}

        # Check histogram crossover (MACD histogram crossing zero)
        histogram = macd_data["histogram"]
        current_histogram = histogram[-1]
        prev_histogram = histogram[-2] if len(histogram) > 1 else current_histogram

        signal = None
        if prev_histogram < 0 and current_histogram > 0:
            signal = "buy"
        elif prev_histogram > 0 and current_histogram < 0:
            signal = "sell"

        return {
            "action": signal or "hold",
            "macd": macd_data["macd"][-1],
            "signal_line": macd_data["signal"][-1],
            "histogram": current_histogram,
            "price": closes[-1]
        }

    async def validate_risk(self, position_size: float, entry_price: float, stop_loss: float) -> bool:
        """Validate risk parameters"""
        return entry_price != 0 and stop_loss != 0 and entry_price != stop_loss
