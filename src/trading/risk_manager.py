"""Risk Management Module"""

from typing import Optional, Dict, Any
from src.trading.portfolio import Portfolio


class RiskManager:
    """Manages trading risk and position sizing"""

    def __init__(self, portfolio: Portfolio, risk_per_trade: float = 0.02, max_drawdown: float = 0.2):
        """
        Initialize risk manager
        
        Args:
            portfolio: Portfolio instance
            risk_per_trade: Risk percentage per trade (default 2%)
            max_drawdown: Maximum drawdown tolerance (default 20%)
        """
        self.portfolio = portfolio
        self.risk_per_trade = risk_per_trade
        self.max_drawdown = max_drawdown
        self.peak_balance = portfolio.initial_balance

    @property
    def current_drawdown(self) -> float:
        """Calculate current drawdown percentage"""
        if self.peak_balance == 0:
            return 0
        drawdown = (self.peak_balance - self.portfolio.equity) / self.peak_balance
        return max(0, drawdown)

    def update_peak_balance(self):
        """Update peak balance if current equity is higher"""
        if self.portfolio.equity > self.peak_balance:
            self.peak_balance = self.portfolio.equity

    def calculate_position_size(self, entry_price: float, stop_loss: float) -> float:
        """
        Calculate position size based on risk
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            
        Returns:
            Position size (amount to buy/sell)
        """
        risk_amount = self.portfolio.total_balance * self.risk_per_trade
        price_risk = abs(entry_price - stop_loss)
        
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        return position_size

    def validate_trade(self, entry_price: float, stop_loss: float, position_size: float) -> Dict[str, Any]:
        """
        Validate trade parameters
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            position_size: Position size
            
        Returns:
            Validation result with status and messages
        """
        issues = []

        # Check drawdown
        if self.current_drawdown >= self.max_drawdown:
            issues.append(f"Maximum drawdown reached: {self.current_drawdown*100:.2f}%")

        # Check stop loss is reasonable
        if entry_price == stop_loss:
            issues.append("Stop loss cannot equal entry price")

        # Check if position size exceeds available capital
        trade_cost = position_size * entry_price
        if trade_cost > self.portfolio.cash:
            issues.append(f"Insufficient capital: need ${trade_cost:.2f}, have ${self.portfolio.cash:.2f}")

        # Check risk reward ratio
        price_risk = abs(entry_price - stop_loss)
        if price_risk > 0:
            risk_reward = price_risk / entry_price
            if risk_reward > 0.1:  # Risk > 10% of entry price
                issues.append(f"High risk per trade: {risk_reward*100:.2f}%")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "position_size": position_size,
            "trade_cost": trade_cost,
            "current_drawdown": self.current_drawdown,
            "risk_amount": self.portfolio.total_balance * self.risk_per_trade
        }

    def get_Kelly_criterion_position_size(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """
        Calculate position size using Kelly Criterion
        
        Args:
            win_rate: Historical win rate (0-1)
            avg_win: Average winning trade
            avg_loss: Average losing trade
            
        Returns:
            Recommended position size fraction (0-1)
        """
        if avg_loss == 0:
            return 0
        
        win_ratio = avg_win / abs(avg_loss)
        kelly = (win_rate * win_ratio - (1 - win_rate)) / win_ratio
        
        # Use half Kelly for safety
        kelly_half = kelly / 2
        
        # Limit to reasonable range
        return max(0, min(kelly_half, 0.25))

    def get_risk_metrics(self) -> Dict[str, Any]:
        """Get current risk metrics"""
        stats = self.portfolio.get_stats()
        
        return {
            "current_drawdown": self.current_drawdown,
            "max_drawdown_limit": self.max_drawdown,
            "peak_balance": self.peak_balance,
            "current_balance": self.portfolio.equity,
            "risk_per_trade": self.risk_per_trade,
            "win_rate": stats["win_rate"],
            "avg_win": stats["avg_win"],
            "avg_loss": stats["avg_loss"],
            "capital_at_risk": self.portfolio.total_balance * self.risk_per_trade,
            "open_positions": stats["open_positions"]
        }

    def print_risk_report(self):
        """Print risk management report"""
        metrics = self.get_risk_metrics()
        
        print("\n" + "="*60)
        print("RISK MANAGEMENT REPORT")
        print("="*60)
        print(f"Current Drawdown:    {metrics['current_drawdown']*100:.2f}%")
        print(f"Max Drawdown Limit:  {metrics['max_drawdown_limit']*100:.2f}%")
        print(f"Peak Balance:        ${metrics['peak_balance']:.2f}")
        print(f"Current Balance:     ${metrics['current_balance']:.2f}")
        print(f"Risk Per Trade:      {metrics['risk_per_trade']*100:.2f}%")
        print(f"Capital at Risk:     ${metrics['capital_at_risk']:.2f}")
        print(f"Win Rate:            {metrics['win_rate']*100:.2f}%")
        print(f"Open Positions:      {metrics['open_positions']}")
        print("="*60 + "\n")
