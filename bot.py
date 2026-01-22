#!/usr/bin/env python3
"""Main entry point for trading bot"""

import asyncio
import argparse
import sys
from src.trading.bot import TradingBot
from src.utils.logger import setup_logger


async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Cryptocurrency Trading Bot")
    parser.add_argument(
        "--exchange",
        default="binance",
        choices=["binance", "coinbase", "kraken"],
        help="Exchange to use"
    )
    parser.add_argument(
        "--mode",
        default="paper",
        choices=["paper", "backtest", "live"],
        help="Trading mode"
    )
    
    args = parser.parse_args()
    
    logger = setup_logger()
    logger.info(f"Starting trading bot with {args.exchange} in {args.mode} mode")
    
    try:
        bot = TradingBot(exchange_name=args.exchange, mode=args.mode)
        await bot.start()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
