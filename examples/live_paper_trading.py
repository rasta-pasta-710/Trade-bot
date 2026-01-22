#!/usr/bin/env python3
"""Example: Live Paper Trading with Real Market Data"""

import asyncio
from src.exchanges.binance import BinanceExchange
from src.trading.portfolio import Portfolio
from src.trading.paper_trading import PaperTradingEngine
from src.trading.risk_manager import RiskManager
from src.trading.metrics import PerformanceMetrics
from src.utils.logger import setup_logger


async def main():
    """Run live paper trading example"""
    logger = setup_logger()
    
    # Initialize components
    initial_balance = 100
    portfolio = Portfolio(initial_balance)
    exchange = BinanceExchange()
    engine = PaperTradingEngine(exchange, portfolio, slippage=0.001, fee=0.001)
    risk_manager = RiskManager(portfolio, risk_per_trade=0.02, max_drawdown=0.2)
    
    try:
        logger.info(f"Starting paper trading with ${initial_balance}")
        
        # Example: Trade BTC/USDT
        symbol = "BTC/USDT"
        
        # Get current price
        ticker = await exchange.get_ticker(symbol)
        current_price = ticker["last"]
        logger.info(f"Current {symbol} price: ${current_price:.2f}")
        
        # Calculate position size
        stop_loss = current_price * 0.95  # 5% stop loss
        position_size = risk_manager.calculate_position_size(current_price, stop_loss)
        
        # Validate trade
        validation = risk_manager.validate_trade(current_price, stop_loss, position_size)
        logger.info(f"Trade validation: {validation}")
        
        if validation["valid"] and position_size > 0:
            # Execute buy
            position = await engine.buy(
                symbol=symbol,
                amount=position_size,
                price=current_price,
                stop_loss=stop_loss,
                take_profit=current_price * 1.05
            )
            logger.info(f"Position opened: {position.to_dict()}")
            
            # Print summary
            engine.print_portfolio_summary()
            risk_manager.print_risk_report()
        else:
            logger.warning(f"Trade validation failed: {validation['issues']}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await exchange.close()


if __name__ == "__main__":
    asyncio.run(main())
