
# Build Prompt

You are a cryptocurrency trading bot developer. Your task is to build a trading bot with the following specifications:

## Core Requirements
- **Initial Capital**: $100
- **Supported Exchanges**: Binance, Coinbase, Kraken (with REST/WebSocket APIs)
- **Trading Modes**: Paper trading, Backtesting, Live trading
- **Primary Language**: Python 3.8+

## Implementation Steps

1. **Setup Environment**
    - Clone repository and install dependencies from `requirements.txt`
    - Configure `.env` with platform API credentials
    - Support multiple AI API providers with abstraction layer

2. **Exchange Integration**
    - Implement factory pattern for exchange instantiation
    - Fetch real-time price feeds, order books, and historical OHLCV data
    - Handle account data (balances, positions, trading history)

3. **Trading Strategy**
    - Develop risk management protocols
    - Implement paper trading mode for validation (minimum 7 days)
    - Support backtesting against historical data

4. **Deployment**
    - Primary: Railway deployment
    - Secondary: Windows VPS failover instance
    - Automated monitoring and logging across environments
    - Infrastructure as Code configuration

5. **Validation Checklist**
    - Paper trading demonstrates positive returns
    - Risk management tests pass
    - Logging operational on both environments
    - Failover tested and functional
    - Approve for live $100 deployment
