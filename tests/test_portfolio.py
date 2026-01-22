"""Tests for Portfolio"""

import pytest
from datetime import datetime
from src.trading.portfolio import Portfolio, Position, Trade


@pytest.fixture
def portfolio():
    """Create a test portfolio"""
    return Portfolio(initial_balance=1000)


def test_portfolio_initialization(portfolio):
    """Test portfolio initialization"""
    assert portfolio.initial_balance == 1000
    assert portfolio.cash == 1000
    assert portfolio.total_balance == 1000
    assert len(portfolio.positions) == 0
    assert len(portfolio.closed_trades) == 0


def test_open_position_buy(portfolio):
    """Test opening a buy position"""
    position = portfolio.open_position(
        symbol="BTC/USDT",
        side="buy",
        amount=0.1,
        entry_price=40000
    )
    
    assert position.symbol == "BTC/USDT"
    assert position.side == "buy"
    assert position.amount == 0.1
    assert position.entry_price == 40000
    assert portfolio.cash == 1000 - (0.1 * 40000)


def test_open_position_insufficient_cash(portfolio):
    """Test opening position with insufficient cash"""
    with pytest.raises(ValueError):
        portfolio.open_position(
            symbol="BTC/USDT",
            side="buy",
            amount=1,
            entry_price=40000
        )


def test_close_position(portfolio):
    """Test closing a position"""
    position = portfolio.open_position(
        symbol="BTC/USDT",
        side="buy",
        amount=0.1,
        entry_price=40000
    )
    
    trade = portfolio.close_position(position.position_id, exit_price=45000)
    
    assert trade.pnl == 0.1 * (45000 - 40000)
    assert trade.pnl_percentage > 0
    assert len(portfolio.closed_trades) == 1
    assert len(portfolio.positions) == 0


def test_portfolio_stats(portfolio):
    """Test portfolio statistics"""
    portfolio.open_position("BTC/USDT", "buy", 0.1, 40000)
    portfolio.close_position(list(portfolio.positions.keys())[0], 45000)
    
    stats = portfolio.get_stats()
    
    assert stats["closed_trades"] == 1
    assert stats["winning_trades"] == 1
    assert stats["win_rate"] == 1.0


def test_portfolio_pnl(portfolio):
    """Test P&L calculation"""
    position = portfolio.open_position("BTC/USDT", "buy", 0.1, 40000)
    portfolio.close_position(position.position_id, 45000)
    
    assert portfolio.total_pnl == 500
    assert portfolio.pnl_percentage == 50
