"""Portfolio Management for Paper Trading"""

from typing import Dict, Optional, Any
from datetime import datetime
from dataclasses import dataclass, field
import uuid


@dataclass
class Position:
    """Represents an open position"""
    symbol: str
    side: str  # 'buy' or 'sell'
    amount: float
    entry_price: float
    entry_time: datetime
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    position_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def unrealized_pnl(self) -> float:
        """Calculate unrealized P&L"""
        if self.side == "buy":
            return self.amount * (self.entry_price - self.entry_price)  # Placeholder
        return 0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "position_id": self.position_id,
            "symbol": self.symbol,
            "side": self.side,
            "amount": self.amount,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time.isoformat(),
            "stop_loss": self.stop_loss,
            "take_profit": self.take_profit
        }


@dataclass
class Trade:
    """Represents a completed trade"""
    symbol: str
    side: str
    amount: float
    entry_price: float
    exit_price: float
    entry_time: datetime
    exit_time: datetime
    pnl: float
    pnl_percentage: float
    trade_id: str = field(default_factory=lambda: str(uuid.uuid4()))

    @property
    def duration(self) -> float:
        """Trade duration in hours"""
        return (self.exit_time - self.entry_time).total_seconds() / 3600

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "trade_id": self.trade_id,
            "symbol": self.symbol,
            "side": self.side,
            "amount": self.amount,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "entry_time": self.entry_time.isoformat(),
            "exit_time": self.exit_time.isoformat(),
            "pnl": self.pnl,
            "pnl_percentage": self.pnl_percentage,
            "duration_hours": self.duration
        }


class Portfolio:
    """Manages paper trading portfolio"""

    def __init__(self, initial_balance: float):
        """Initialize portfolio"""
        self.initial_balance = initial_balance
        self.cash = initial_balance
        self.positions: Dict[str, Position] = {}
        self.closed_trades: list = []
        self.transaction_history: list = []

    @property
    def total_balance(self) -> float:
        """Total portfolio value (cash + positions)"""
        position_value = sum(pos.amount * pos.entry_price for pos in self.positions.values())
        return self.cash + position_value

    @property
    def equity(self) -> float:
        """Current equity"""
        return self.total_balance

    @property
    def unrealized_pnl(self) -> float:
        """Total unrealized P&L"""
        return sum(pos.unrealized_pnl for pos in self.positions.values())

    @property
    def realized_pnl(self) -> float:
        """Total realized P&L from closed trades"""
        return sum(trade.pnl for trade in self.closed_trades)

    @property
    def total_pnl(self) -> float:
        """Total P&L (realized + unrealized)"""
        return self.realized_pnl + self.unrealized_pnl

    @property
    def pnl_percentage(self) -> float:
        """P&L as percentage of initial balance"""
        if self.initial_balance == 0:
            return 0
        return (self.total_pnl / self.initial_balance) * 100

    def open_position(self, symbol: str, side: str, amount: float, entry_price: float,
                     stop_loss: Optional[float] = None, take_profit: Optional[float] = None) -> Position:
        """Open a new position"""
        cost = amount * entry_price
        if side == "buy" and cost > self.cash:
            raise ValueError(f"Insufficient cash: need {cost}, have {self.cash}")

        position = Position(
            symbol=symbol,
            side=side,
            amount=amount,
            entry_price=entry_price,
            entry_time=datetime.now(),
            stop_loss=stop_loss,
            take_profit=take_profit
        )

        if side == "buy":
            self.cash -= cost
        else:  # sell
            self.cash += cost

        self.positions[position.position_id] = position
        self.transaction_history.append({
            "type": "open",
            "position": position.to_dict(),
            "timestamp": datetime.now().isoformat()
        })

        return position

    def close_position(self, position_id: str, exit_price: float) -> Trade:
        """Close an open position"""
        if position_id not in self.positions:
            raise ValueError(f"Position {position_id} not found")

        position = self.positions[position_id]
        exit_time = datetime.now()

        # Calculate P&L
        if position.side == "buy":
            pnl = position.amount * (exit_price - position.entry_price)
            self.cash += position.amount * exit_price
        else:  # sell
            pnl = position.amount * (position.entry_price - exit_price)
            self.cash -= position.amount * exit_price

        pnl_percentage = (pnl / (position.amount * position.entry_price)) * 100 if position.entry_price > 0 else 0

        trade = Trade(
            symbol=position.symbol,
            side=position.side,
            amount=position.amount,
            entry_price=position.entry_price,
            exit_price=exit_price,
            entry_time=position.entry_time,
            exit_time=exit_time,
            pnl=pnl,
            pnl_percentage=pnl_percentage
        )

        self.closed_trades.append(trade)
        del self.positions[position_id]

        self.transaction_history.append({
            "type": "close",
            "trade": trade.to_dict(),
            "timestamp": exit_time.isoformat()
        })

        return trade

    def get_open_positions(self) -> Dict[str, Position]:
        """Get all open positions"""
        return self.positions.copy()

    def get_closed_trades(self) -> list:
        """Get all closed trades"""
        return self.closed_trades.copy()

    def get_stats(self) -> Dict[str, Any]:
        """Get portfolio statistics"""
        winning_trades = [t for t in self.closed_trades if t.pnl > 0]
        losing_trades = [t for t in self.closed_trades if t.pnl < 0]

        return {
            "initial_balance": self.initial_balance,
            "current_balance": self.total_balance,
            "cash": self.cash,
            "total_pnl": self.total_pnl,
            "pnl_percentage": self.pnl_percentage,
            "realized_pnl": self.realized_pnl,
            "unrealized_pnl": self.unrealized_pnl,
            "open_positions": len(self.positions),
            "closed_trades": len(self.closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": len(winning_trades) / len(self.closed_trades) if self.closed_trades else 0,
            "avg_win": sum(t.pnl for t in winning_trades) / len(winning_trades) if winning_trades else 0,
            "avg_loss": sum(t.pnl for t in losing_trades) / len(losing_trades) if losing_trades else 0
        }
