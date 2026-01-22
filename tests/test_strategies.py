"""Tests for Strategies"""

import pytest
from src.strategies.strategies import SMAcrossoverStrategy, RSIStrategy


@pytest.mark.asyncio
async def test_sma_strategy_initialization():
    """Test SMA strategy initialization"""
    strategy = SMAcrossoverStrategy(fast_period=10, slow_period=20)
    
    assert strategy.name == "SMA Crossover"
    assert strategy.fast_period == 10
    assert strategy.slow_period == 20


@pytest.mark.asyncio
async def test_sma_crossover():
    """Test SMA crossover analysis"""
    strategy = SMAcrossoverStrategy(fast_period=3, slow_period=5)
    
    # Create test data: uptrend followed by crossover
    closes = [100, 101, 102, 103, 104, 105, 104, 103, 102]
    market_data = {"closes": closes}
    
    result = await strategy.analyze(market_data)
    
    assert "action" in result
    assert result["action"] in ["buy", "sell", "hold"]


@pytest.mark.asyncio
async def test_rsi_strategy():
    """Test RSI strategy"""
    strategy = RSIStrategy(rsi_period=14, overbought=70, oversold=30)
    
    # Create test data
    closes = [100 + i * 0.5 for i in range(50)]
    market_data = {"closes": closes}
    
    result = await strategy.analyze(market_data)
    
    assert "action" in result
    assert "rsi" in result


def test_calculate_sma():
    """Test SMA calculation"""
    from src.strategies.base_strategy import BaseStrategy
    
    prices = [100, 101, 102, 103, 104]
    sma = BaseStrategy.calculate_sma(prices, period=3)
    
    assert len(sma) == 3
    assert sma[0] == pytest.approx(101)  # (100 + 101 + 102) / 3
    assert sma[1] == pytest.approx(102)  # (101 + 102 + 103) / 3
    assert sma[2] == pytest.approx(103)  # (102 + 103 + 104) / 3


def test_calculate_rsi():
    """Test RSI calculation"""
    from src.strategies.base_strategy import BaseStrategy
    
    prices = [100, 101, 102, 103, 104, 103, 102, 101, 100]
    rsi = BaseStrategy.calculate_rsi(prices, period=5)
    
    assert len(rsi) > 0
    assert all(0 <= value <= 100 for value in rsi)
