"""Main Trading Bot"""

import asyncio
from typing import Optional, Dict, Any
from src.utils.config import Config
from src.utils.logger import setup_logger
from src.exchanges.factory import ExchangeFactory


class TradingBot:
    """Main trading bot class"""

    def __init__(self, exchange_name: str = "binance", mode: str = "paper"):
        """
        Initialize trading bot
        
        Args:
            exchange_name: Name of exchange to use
            mode: Trading mode (paper, backtest, live)
        """
        self.config = Config()
        self.logger = setup_logger("trading_bot")
        self.exchange_name = exchange_name
        self.mode = mode
        self.exchange = None

    async def initialize(self):
        """Initialize bot and exchange connection"""
        try:
            self.logger.info(f"Initializing trading bot on {self.exchange_name} ({self.mode} mode)")
            
            # Get exchange credentials
            credentials = self.config.get_exchange_credentials(self.exchange_name)
            
            # Create exchange instance
            self.exchange = ExchangeFactory.create(self.exchange_name, **credentials)
            
            self.logger.info("Bot initialized successfully")
        except Exception as e:
            self.logger.error(f"Failed to initialize bot: {e}")
            raise

    async def start(self):
        """Start trading bot"""
        try:
            await self.initialize()
            self.logger.info(f"Starting trading bot in {self.mode} mode")
            
            # TODO: Implement trading loop
            await self._trading_loop()
            
        except Exception as e:
            self.logger.error(f"Error running bot: {e}")
            raise
        finally:
            if self.exchange:
                await self.exchange.close()

    async def _trading_loop(self):
        """Main trading loop"""
        # TODO: Implement trading logic
        pass

    async def stop(self):
        """Stop trading bot"""
        self.logger.info("Stopping trading bot")
        if self.exchange:
            await self.exchange.close()
