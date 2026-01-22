"""Configuration Management"""

import os
from dotenv import load_dotenv
from typing import Optional, Any


class Config:
    """Configuration manager for trading bot"""

    def __init__(self, env_file: str = ".env"):
        """Load environment configuration"""
        if os.path.exists(env_file):
            load_dotenv(env_file)

    @staticmethod
    def get(key: str, default: Any = None) -> Optional[str]:
        """Get configuration value"""
        return os.getenv(key, default)

    @staticmethod
    def get_int(key: str, default: int = 0) -> int:
        """Get integer configuration value"""
        value = os.getenv(key, default)
        return int(value) if value else default

    @staticmethod
    def get_bool(key: str, default: bool = False) -> bool:
        """Get boolean configuration value"""
        value = os.getenv(key, default)
        if isinstance(value, bool):
            return value
        return value.lower() in ('true', '1', 'yes') if value else default

    @staticmethod
    def get_exchange_credentials(exchange_name: str) -> dict:
        """Get exchange API credentials"""
        exchange_upper = exchange_name.upper()
        
        if exchange_name == "binance":
            return {
                "api_key": os.getenv(f"{exchange_upper}_API_KEY"),
                "api_secret": os.getenv(f"{exchange_upper}_API_SECRET"),
            }
        elif exchange_name == "coinbase":
            return {
                "api_key": os.getenv(f"{exchange_upper}_API_KEY"),
                "api_secret": os.getenv(f"{exchange_upper}_API_SECRET"),
                "passphrase": os.getenv(f"{exchange_upper}_PASSPHRASE"),
            }
        elif exchange_name == "kraken":
            return {
                "api_key": os.getenv(f"{exchange_upper}_API_KEY"),
                "api_secret": os.getenv(f"{exchange_upper}_API_SECRET"),
            }
        else:
            raise ValueError(f"Unknown exchange: {exchange_name}")
