#!/usr/bin/env python3
"""Example: Backtest with SMA Crossover Strategy"""

import asyncio
from src.trading.backtester import Backtester, BacktestExchange
from src.trading.paper_trading import PaperTradingEngine
from src.strategies.strategies import SMAcrossoverStrategy
from src.utils.logger import setup_logger


async def sma_strategy(index: int, exchange: BacktestExchange, engine: PaperTradingEngine):
    """SMA Crossover trading logic"""
    strategy = SMAcrossoverStrategy(fast_period=10, slow_period=20)
    
    # Get OHLCV data
    try:
        ohlcv = await exchange.get_ohlcv("BTC/USDT")
        if not ohlcv:
            return
        
        closes = [candle[4] for candle in ohlcv]
        market_data = {"closes": closes}
        
        # Analyze
        signal = await strategy.analyze(market_data)
        
        if signal["action"] == "buy" and not engine.portfolio.positions:
            # Buy signal
            current_price = closes[-1]
            stop_loss = current_price * 0.95
            amount = 0.01  # 0.01 BTC
            
            position = await engine.buy("BTC/USDT", amount, current_price, stop_loss=stop_loss)
        
        elif signal["action"] == "sell" and engine.portfolio.positions:
            # Sell signal - close all positions
            for position_id in list(engine.portfolio.positions.keys()):
                current_price = closes[-1]
                await engine.close(position_id, current_price)
    
    except Exception as e:
        pass  # Ignore errors during backtest


async def main():
    """Run backtest example"""
    logger = setup_logger()
    backtester = Backtester(initial_balance=100)
    
    try:
        logger.info("Generating sample OHLCV data for backtest...")
        
        # Generate sample OHLCV data (5 days of hourly candles)
        import time
        ohlcv_data = {"BTC/USDT": []}
        base_price = 40000
        current_time = int(time.time()) * 1000
        
        for i in range(120):  # 5 days * 24 hours
            open_p = base_price + (i % 10) * 100
            close_p = open_p + (i % 5 - 2) * 100
            high_p = max(open_p, close_p) + 200
            low_p = min(open_p, close_p) - 200
            volume = 100 + (i % 50)
            
            ohlcv_data["BTC/USDT"].append([
                current_time + i * 3600000,
                open_p, high_p, low_p, close_p, volume
            ])
        
        logger.info("Running backtest...")
        results = await backtester.run_backtest(
            ohlcv_data=ohlcv_data,
            strategy_fn=sma_strategy,
            slippage=0.001,
            fee=0.001
        )
        
        backtester.print_backtest_results(results)
        
    except Exception as e:
        logger.error(f"Backtest error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
