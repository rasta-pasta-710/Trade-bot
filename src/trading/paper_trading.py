"""Paper Trading Engine"""

import asyncio
from typing import Dict, Optional, Callable, Any
from datetime import datetime
from src.trading.portfolio import Portfolio, Position, Trade
from src.utils.logger import setup_logger


class PaperTradingEngine:
    """Executes paper trades with real market data"""

    def __init__(self, exchange, portfolio: Portfolio, slippage: float = 0.001, fee: float = 0.001):
        """
        Initialize paper trading engine
        
        Args:
            exchange: Exchange instance for market data
            portfolio: Portfolio instance to track trades
            slippage: Slippage as percentage (default 0.1%)
            fee: Trading fee as percentage (default 0.1%)
        """
        self.exchange = exchange
        self.portfolio = portfolio
        self.slippage = slippage
        self.fee = fee
        self.logger = setup_logger("paper_trading")
        self.open_orders: Dict[str, Dict[str, Any]] = {}

    async def get_current_price(self, symbol: str) -> float:
        """Get current market price"""
        try:
            ticker = await self.exchange.get_ticker(symbol)
            return ticker["last"]
        except Exception as e:
            self.logger.error(f"Failed to get price for {symbol}: {e}")
            raise

    async def buy(self, symbol: str, amount: float, price: Optional[float] = None,
                 stop_loss: Optional[float] = None, take_profit: Optional[float] = None) -> Position:
        """Execute a buy order"""
        try:
            if price is None:
                price = await self.get_current_price(symbol)

            # Apply slippage
            actual_price = price * (1 + self.slippage)
            
            # Apply fee
            fee_amount = actual_price * amount * self.fee
            actual_price += (fee_amount / amount)

            self.logger.info(f"BUY {amount} {symbol} @ {actual_price:.2f}")
            
            position = self.portfolio.open_position(
                symbol=symbol,
                side="buy",
                amount=amount,
                entry_price=actual_price,
                stop_loss=stop_loss,
                take_profit=take_profit
            )

            self.logger.info(f"Position opened: {position.position_id}")
            return position

        except Exception as e:
            self.logger.error(f"Failed to execute buy order: {e}")
            raise

    async def sell(self, symbol: str, amount: float, price: Optional[float] = None) -> Position:
        """Execute a sell order"""
        try:
            if price is None:
                price = await self.get_current_price(symbol)

            # Apply slippage
            actual_price = price * (1 - self.slippage)
            
            # Apply fee
            fee_amount = actual_price * amount * self.fee
            actual_price -= (fee_amount / amount)

            self.logger.info(f"SELL {amount} {symbol} @ {actual_price:.2f}")
            
            position = self.portfolio.open_position(
                symbol=symbol,
                side="sell",
                amount=amount,
                entry_price=actual_price
            )

            self.logger.info(f"Short position opened: {position.position_id}")
            return position

        except Exception as e:
            self.logger.error(f"Failed to execute sell order: {e}")
            raise

    async def close(self, position_id: str, price: Optional[float] = None) -> Trade:
        """Close a position"""
        try:
            position = self.portfolio.positions.get(position_id)
            if not position:
                raise ValueError(f"Position {position_id} not found")

            if price is None:
                price = await self.get_current_price(position.symbol)

            # Apply slippage and fee
            if position.side == "buy":
                actual_price = price * (1 - self.slippage)
            else:
                actual_price = price * (1 + self.slippage)

            fee_amount = actual_price * position.amount * self.fee
            actual_price -= (fee_amount / position.amount) if position.side == "buy" else -1 * (fee_amount / position.amount)

            self.logger.info(f"CLOSE {position.side.upper()} {position.symbol} @ {actual_price:.2f}")

            trade = self.portfolio.close_position(position_id, actual_price)
            self.logger.info(f"Trade closed - P&L: ${trade.pnl:.2f} ({trade.pnl_percentage:.2f}%)")

            return trade

        except Exception as e:
            self.logger.error(f"Failed to close position: {e}")
            raise

    async def check_stop_losses_and_take_profits(self):
        """Check and execute stop losses and take profits"""
        positions_to_close = []

        for position_id, position in self.portfolio.positions.items():
            current_price = await self.get_current_price(position.symbol)

            # Check stop loss
            if position.stop_loss and ((position.side == "buy" and current_price <= position.stop_loss) or
                                       (position.side == "sell" and current_price >= position.stop_loss)):
                self.logger.info(f"Stop loss triggered for {position_id}")
                positions_to_close.append((position_id, position.stop_loss))

            # Check take profit
            elif position.take_profit and ((position.side == "buy" and current_price >= position.take_profit) or
                                           (position.side == "sell" and current_price <= position.take_profit)):
                self.logger.info(f"Take profit triggered for {position_id}")
                positions_to_close.append((position_id, position.take_profit))

        # Close triggered positions
        for position_id, price in positions_to_close:
            await self.close(position_id, price)

    def get_portfolio_stats(self) -> Dict[str, Any]:
        """Get portfolio statistics"""
        return self.portfolio.get_stats()

    def print_portfolio_summary(self):
        """Print portfolio summary"""
        stats = self.get_portfolio_stats()
        
        print("\n" + "="*60)
        print("PAPER TRADING PORTFOLIO SUMMARY")
        print("="*60)
        print(f"Initial Balance:     ${stats['initial_balance']:.2f}")
        print(f"Current Balance:     ${stats['current_balance']:.2f}")
        print(f"Cash:                ${stats['cash']:.2f}")
        print(f"Total P&L:           ${stats['total_pnl']:.2f}")
        print(f"P&L %:               {stats['pnl_percentage']:.2f}%")
        print(f"Realized P&L:        ${stats['realized_pnl']:.2f}")
        print(f"Unrealized P&L:      ${stats['unrealized_pnl']:.2f}")
        print(f"Open Positions:      {stats['open_positions']}")
        print(f"Closed Trades:       {stats['closed_trades']}")
        print(f"Win Rate:            {stats['win_rate']*100:.2f}%")
        if stats['winning_trades'] > 0:
            print(f"Avg Win:             ${stats['avg_win']:.2f}")
        if stats['losing_trades'] > 0:
            print(f"Avg Loss:            ${stats['avg_loss']:.2f}")
        print("="*60 + "\n")
