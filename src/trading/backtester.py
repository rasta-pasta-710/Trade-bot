"""Backtesting Engine"""

from typing import List, Dict, Any, Callable, Optional
from datetime import datetime, timedelta
import asyncio
from src.trading.portfolio import Portfolio
from src.trading.paper_trading import PaperTradingEngine
from src.utils.logger import setup_logger


class BacktestExchange:
    """Mock exchange for backtesting using historical data"""

    def __init__(self, ohlcv_data: Dict[str, List[List[Any]]]):
        """
        Initialize backtest exchange
        
        Args:
            ohlcv_data: Historical OHLCV data {symbol: [[time, o, h, l, c, v], ...]}
        """
        self.ohlcv_data = ohlcv_data
        self.current_index = 0

    def set_current_index(self, index: int):
        """Set current position in historical data"""
        self.current_index = index

    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """Get ticker at current index"""
        if symbol not in self.ohlcv_data or len(self.ohlcv_data[symbol]) <= self.current_index:
            raise ValueError(f"No data for {symbol} at index {self.current_index}")

        candle = self.ohlcv_data[symbol][self.current_index]
        return {
            "last": candle[4],  # close
            "bid": candle[3],   # low
            "ask": candle[2],   # high
            "high": candle[2],
            "low": candle[3],
            "timestamp": candle[0],
            "volume": candle[5]
        }

    async def get_order_book(self, symbol: str, limit: int = 20) -> Dict[str, Any]:
        """Get order book at current index"""
        ticker = await self.get_ticker(symbol)
        return {
            "bids": [[ticker["bid"], 1.0]],
            "asks": [[ticker["ask"], 1.0]],
            "timestamp": ticker["timestamp"],
            "symbol": symbol
        }

    async def get_ohlcv(self, symbol: str, timeframe: str = "1h", limit: int = 100) -> List[List[Any]]:
        """Get OHLCV data"""
        if symbol not in self.ohlcv_data:
            raise ValueError(f"No data for {symbol}")
        
        start_idx = max(0, self.current_index - limit)
        return self.ohlcv_data[symbol][start_idx:self.current_index+1]

    async def place_order(self, symbol: str, side: str, order_type: str, amount: float, price: Optional[float] = None) -> Dict[str, Any]:
        """Place order (backtesting)"""
        return {"status": "paper_order"}

    async def cancel_order(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Cancel order"""
        return {"status": "canceled"}

    async def get_order_status(self, order_id: str, symbol: str) -> Dict[str, Any]:
        """Get order status"""
        return {"status": "closed"}

    async def close(self):
        """Close connection"""
        pass


class Backtester:
    """Run backtests on historical data"""

    def __init__(self, initial_balance: float = 100):
        """Initialize backtester"""
        self.initial_balance = initial_balance
        self.logger = setup_logger("backtester")

    async def run_backtest(self, 
                          ohlcv_data: Dict[str, List[List[Any]]],
                          strategy_fn: Callable,
                          slippage: float = 0.001,
                          fee: float = 0.001) -> Dict[str, Any]:
        """
        Run backtest with given strategy
        
        Args:
            ohlcv_data: Historical OHLCV data
            strategy_fn: Async strategy function(index, exchange, engine) -> actions
            slippage: Slippage percentage
            fee: Trading fee percentage
            
        Returns:
            Backtest results
        """
        portfolio = Portfolio(self.initial_balance)
        exchange = BacktestExchange(ohlcv_data)
        engine = PaperTradingEngine(exchange, portfolio, slippage, fee)

        # Get number of candles
        first_symbol = list(ohlcv_data.keys())[0]
        num_candles = len(ohlcv_data[first_symbol])

        self.logger.info(f"Starting backtest with {num_candles} candles")

        # Run through each candle
        for i in range(num_candles):
            exchange.set_current_index(i)
            
            # Call strategy
            try:
                await strategy_fn(i, exchange, engine)
            except Exception as e:
                self.logger.error(f"Strategy error at candle {i}: {e}")
                continue

            # Check stop losses and take profits
            try:
                await engine.check_stop_losses_and_take_profits()
            except Exception as e:
                self.logger.debug(f"Error checking stops at candle {i}: {e}")

        # Calculate performance metrics
        stats = portfolio.get_stats()
        
        results = {
            "initial_balance": self.initial_balance,
            "final_balance": portfolio.equity,
            "total_return": portfolio.total_pnl,
            "return_percentage": stats["pnl_percentage"],
            "closed_trades": len(stats["closed_trades"]),
            "win_rate": stats["win_rate"],
            "max_win": max([t.pnl for t in portfolio.closed_trades]) if portfolio.closed_trades else 0,
            "max_loss": min([t.pnl for t in portfolio.closed_trades]) if portfolio.closed_trades else 0,
            "avg_win": stats["avg_win"],
            "avg_loss": stats["avg_loss"],
            "sharpe_ratio": self._calculate_sharpe_ratio(portfolio),
            "max_drawdown": self._calculate_max_drawdown(portfolio),
            "profit_factor": self._calculate_profit_factor(portfolio)
        }

        self.logger.info(f"Backtest complete - Return: {results['return_percentage']:.2f}%")
        
        return results

    def _calculate_sharpe_ratio(self, portfolio: Portfolio) -> float:
        """Calculate Sharpe ratio"""
        if len(portfolio.closed_trades) < 2:
            return 0

        returns = [t.pnl for t in portfolio.closed_trades]
        avg_return = sum(returns) / len(returns)
        variance = sum((r - avg_return) ** 2 for r in returns) / len(returns)
        std_dev = variance ** 0.5

        if std_dev == 0:
            return 0

        # Assuming 252 trading days per year
        return (avg_return / std_dev) * (252 ** 0.5)

    def _calculate_max_drawdown(self, portfolio: Portfolio) -> float:
        """Calculate maximum drawdown"""
        if not portfolio.closed_trades:
            return 0

        peak = self.initial_balance
        max_dd = 0

        balance = self.initial_balance
        for trade in portfolio.closed_trades:
            balance += trade.pnl
            if balance > peak:
                peak = balance
            dd = (peak - balance) / peak
            if dd > max_dd:
                max_dd = dd

        return max_dd

    def _calculate_profit_factor(self, portfolio: Portfolio) -> float:
        """Calculate profit factor (gross wins / gross losses)"""
        if not portfolio.closed_trades:
            return 0

        gross_wins = sum(t.pnl for t in portfolio.closed_trades if t.pnl > 0)
        gross_losses = abs(sum(t.pnl for t in portfolio.closed_trades if t.pnl < 0))

        if gross_losses == 0:
            return float('inf') if gross_wins > 0 else 0

        return gross_wins / gross_losses

    def print_backtest_results(self, results: Dict[str, Any]):
        """Print backtest results"""
        print("\n" + "="*60)
        print("BACKTEST RESULTS")
        print("="*60)
        print(f"Initial Balance:     ${results['initial_balance']:.2f}")
        print(f"Final Balance:       ${results['final_balance']:.2f}")
        print(f"Total Return:        ${results['total_return']:.2f}")
        print(f"Return %:            {results['return_percentage']:.2f}%")
        print(f"Closed Trades:       {results['closed_trades']}")
        print(f"Win Rate:            {results['win_rate']*100:.2f}%")
        print(f"Avg Win:             ${results['avg_win']:.2f}")
        print(f"Avg Loss:            ${results['avg_loss']:.2f}")
        print(f"Max Win:             ${results['max_win']:.2f}")
        print(f"Max Loss:            ${results['max_loss']:.2f}")
        print(f"Sharpe Ratio:        {results['sharpe_ratio']:.2f}")
        print(f"Max Drawdown:        {results['max_drawdown']*100:.2f}%")
        print(f"Profit Factor:       {results['profit_factor']:.2f}")
        print("="*60 + "\n")
