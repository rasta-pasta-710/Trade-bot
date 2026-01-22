"""Performance Metrics and Reporting"""

from typing import Dict, Any, List
from src.trading.portfolio import Portfolio, Trade
import statistics


class PerformanceMetrics:
    """Calculate and report performance metrics"""

    @staticmethod
    def calculate_sharpe_ratio(trades: List[Trade], risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe Ratio
        
        Args:
            trades: List of completed trades
            risk_free_rate: Annual risk-free rate (default 2%)
            
        Returns:
            Sharpe ratio
        """
        if len(trades) < 2:
            return 0

        returns = [t.pnl for t in trades]
        avg_return = statistics.mean(returns)
        std_dev = statistics.stdev(returns) if len(returns) > 1 else 0

        if std_dev == 0:
            return 0

        # Annualize (assuming 252 trading days)
        return (avg_return * 252 - risk_free_rate) / (std_dev * (252 ** 0.5))

    @staticmethod
    def calculate_sortino_ratio(trades: List[Trade], risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sortino Ratio (similar to Sharpe but only penalizes downside volatility)
        
        Args:
            trades: List of completed trades
            risk_free_rate: Annual risk-free rate
            
        Returns:
            Sortino ratio
        """
        if len(trades) < 2:
            return 0

        returns = [t.pnl for t in trades]
        avg_return = statistics.mean(returns)
        downside_returns = [r for r in returns if r < 0]

        if not downside_returns:
            downside_std = 0
        else:
            downside_std = (sum(r ** 2 for r in downside_returns) / len(downside_returns)) ** 0.5

        if downside_std == 0:
            return float('inf') if avg_return > 0 else 0

        return (avg_return * 252 - risk_free_rate) / (downside_std * (252 ** 0.5))

    @staticmethod
    def calculate_calmar_ratio(trades: List[Trade], initial_balance: float) -> float:
        """Calculate Calmar Ratio (return / max drawdown)"""
        if not trades or initial_balance == 0:
            return 0

        total_return = sum(t.pnl for t in trades) / initial_balance
        max_drawdown = PerformanceMetrics.calculate_max_drawdown(trades, initial_balance)

        if max_drawdown == 0:
            return float('inf') if total_return > 0 else 0

        return total_return / max_drawdown

    @staticmethod
    def calculate_max_drawdown(trades: List[Trade], initial_balance: float) -> float:
        """Calculate maximum drawdown"""
        if not trades:
            return 0

        peak = initial_balance
        max_dd = 0
        balance = initial_balance

        for trade in trades:
            balance += trade.pnl
            if balance > peak:
                peak = balance
            dd = (peak - balance) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd

        return max_dd

    @staticmethod
    def calculate_profit_factor(trades: List[Trade]) -> float:
        """Calculate Profit Factor (gross wins / gross losses)"""
        if not trades:
            return 0

        gross_wins = sum(t.pnl for t in trades if t.pnl > 0)
        gross_losses = abs(sum(t.pnl for t in trades if t.pnl < 0))

        if gross_losses == 0:
            return float('inf') if gross_wins > 0 else 0

        return gross_wins / gross_losses

    @staticmethod
    def calculate_recovery_factor(trades: List[Trade], initial_balance: float) -> float:
        """Calculate Recovery Factor (total return / max drawdown)"""
        if not trades or initial_balance == 0:
            return 0

        total_return = sum(t.pnl for t in trades)
        max_drawdown = PerformanceMetrics.calculate_max_drawdown(trades, initial_balance)

        if max_drawdown == 0:
            return float('inf') if total_return > 0 else 0

        return total_return / (max_drawdown * initial_balance)

    @staticmethod
    def get_full_report(portfolio: Portfolio) -> Dict[str, Any]:
        """Generate full performance report"""
        trades = portfolio.closed_trades
        stats = portfolio.get_stats()

        if not trades:
            return {
                "summary": stats,
                "metrics": {
                    "sharpe_ratio": 0,
                    "sortino_ratio": 0,
                    "calmar_ratio": 0,
                    "max_drawdown": 0,
                    "profit_factor": 0,
                    "recovery_factor": 0
                },
                "trades": []
            }

        return {
            "summary": stats,
            "metrics": {
                "sharpe_ratio": PerformanceMetrics.calculate_sharpe_ratio(trades),
                "sortino_ratio": PerformanceMetrics.calculate_sortino_ratio(trades),
                "calmar_ratio": PerformanceMetrics.calculate_calmar_ratio(trades, portfolio.initial_balance),
                "max_drawdown": PerformanceMetrics.calculate_max_drawdown(trades, portfolio.initial_balance),
                "profit_factor": PerformanceMetrics.calculate_profit_factor(trades),
                "recovery_factor": PerformanceMetrics.calculate_recovery_factor(trades, portfolio.initial_balance)
            },
            "trades": [t.to_dict() for t in trades]
        }

    @staticmethod
    def print_full_report(portfolio: Portfolio):
        """Print full performance report"""
        report = PerformanceMetrics.get_full_report(portfolio)
        stats = report["summary"]
        metrics = report["metrics"]
        trades = report["trades"]

        print("\n" + "="*70)
        print("FULL PERFORMANCE REPORT".center(70))
        print("="*70)

        print("\n--- PORTFOLIO SUMMARY ---")
        print(f"Initial Balance:           ${stats['initial_balance']:>12.2f}")
        print(f"Final Balance:             ${stats['initial_balance'] + stats['total_pnl']:>12.2f}")
        print(f"Total Return:              ${stats['total_pnl']:>12.2f}")
        print(f"Return %:                  {stats['pnl_percentage']:>12.2f}%")

        print("\n--- TRADE STATISTICS ---")
        print(f"Total Trades:              {stats['closed_trades']:>12d}")
        print(f"Winning Trades:            {stats['winning_trades']:>12d}")
        print(f"Losing Trades:             {stats['losing_trades']:>12d}")
        print(f"Win Rate:                  {stats['win_rate']*100:>12.2f}%")
        print(f"Average Win:               ${stats['avg_win']:>12.2f}")
        print(f"Average Loss:              ${stats['avg_loss']:>12.2f}")

        print("\n--- RISK METRICS ---")
        print(f"Max Drawdown:              {metrics['max_drawdown']*100:>12.2f}%")
        print(f"Profit Factor:             {metrics['profit_factor']:>12.2f}")

        print("\n--- ADVANCED METRICS ---")
        print(f"Sharpe Ratio:              {metrics['sharpe_ratio']:>12.2f}")
        print(f"Sortino Ratio:             {metrics['sortino_ratio']:>12.2f}")
        print(f"Calmar Ratio:              {metrics['calmar_ratio']:>12.2f}")
        print(f"Recovery Factor:           {metrics['recovery_factor']:>12.2f}")

        if trades:
            print("\n--- BEST / WORST TRADES ---")
            best_trade = max(trades, key=lambda t: t["pnl"])
            worst_trade = min(trades, key=lambda t: t["pnl"])
            print(f"Best Trade:                ${best_trade['pnl']:>12.2f} ({best_trade['pnl_percentage']:.2f}%)")
            print(f"Worst Trade:               ${worst_trade['pnl']:>12.2f} ({worst_trade['pnl_percentage']:.2f}%)")

            avg_duration = sum(t["duration_hours"] for t in trades) / len(trades)
            print(f"Avg Trade Duration:        {avg_duration:>12.2f}h")

        print("\n" + "="*70 + "\n")
