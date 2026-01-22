"""Tests for Risk Manager"""

import pytest
from src.trading.portfolio import Portfolio
from src.trading.risk_manager import RiskManager


@pytest.fixture
def risk_manager():
    """Create test risk manager"""
    portfolio = Portfolio(initial_balance=1000)
    return RiskManager(portfolio, risk_per_trade=0.02, max_drawdown=0.2)


def test_risk_manager_initialization(risk_manager):
    """Test risk manager initialization"""
    assert risk_manager.risk_per_trade == 0.02
    assert risk_manager.max_drawdown == 0.2
    assert risk_manager.peak_balance == 1000


def test_calculate_position_size(risk_manager):
    """Test position size calculation"""
    position_size = risk_manager.calculate_position_size(
        entry_price=40000,
        stop_loss=38000
    )
    
    # Risk amount = 1000 * 0.02 = 20
    # Price risk = 40000 - 38000 = 2000
    # Position size = 20 / 2000 = 0.01
    assert position_size == pytest.approx(0.01)


def test_validate_trade(risk_manager):
    """Test trade validation"""
    result = risk_manager.validate_trade(
        entry_price=40000,
        stop_loss=38000,
        position_size=0.01
    )
    
    assert result["valid"] == True
    assert len(result["issues"]) == 0


def test_validate_trade_insufficient_capital(risk_manager):
    """Test validation with insufficient capital"""
    result = risk_manager.validate_trade(
        entry_price=40000,
        stop_loss=38000,
        position_size=1.0  # Would need 40000
    )
    
    assert result["valid"] == False
    assert len(result["issues"]) > 0


def test_drawdown_calculation(risk_manager):
    """Test drawdown calculation"""
    portfolio = risk_manager.portfolio
    
    # Add a losing trade
    position = portfolio.open_position("BTC/USDT", "buy", 0.1, 40000)
    portfolio.close_position(position.position_id, 35000)
    
    # Update peak balance and check drawdown
    risk_manager.update_peak_balance()
    drawdown = risk_manager.current_drawdown
    
    assert drawdown > 0
