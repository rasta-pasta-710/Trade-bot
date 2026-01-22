# Paper Trading System Documentation

Complete paper trading system built with public market data from CCXT. Fully functional with real-time price data, backtesting, and risk management.

## Features

### ✅ Real Market Data (Public APIs)
- **Live price feeds** from Binance, Coinbase, Kraken
- **Order book data** with real bid/ask spreads
- **OHLCV candles** for technical analysis
- No authentication required - works with public endpoints

### ✅ Paper Trading Engine
- **Order simulation** with realistic slippage and fees
- **Position tracking** with entry/exit prices and P&L
- **Stop-loss & take-profit** automation
- **Portfolio balancing** with cash management

### ✅ Risk Management
- **Position sizing** based on risk per trade
- **Drawdown tracking** with maximum limit enforcement
- **Risk validation** before trade execution
- **Kelly Criterion** for optimal position sizing

### ✅ Backtesting Engine
- **Historical data replay** with OHLCV candles
- **Strategy simulation** against past prices
- **Performance metrics** (Sharpe, Sortino, Calmar ratios)
- **Trade-by-trade analysis** with detailed reporting

### ✅ Trading Strategies
1. **SMA Crossover** - Simple Moving Average crossover signals
2. **RSI Strategy** - Overbought/Oversold reversal trades
3. **MACD Strategy** - Moving Average Convergence Divergence signals

### ✅ Advanced Analytics
- **Sharpe Ratio** - Risk-adjusted returns
- **Sortino Ratio** - Downside risk measure
- **Calmar Ratio** - Return per unit of drawdown
- **Profit Factor** - Gross wins / gross losses
- **Win Rate** - Percentage of profitable trades
- **Max Drawdown** - Peak to trough decline

## Architecture

```
src/
├── exchanges/                  # CCXT wrapper implementations
│   ├── base.py                # Abstract exchange interface
│   ├── factory.py             # Exchange factory pattern
│   ├── binance.py             # Binance CCXT integration
│   ├── coinbase.py            # Coinbase CCXT integration
│   └── kraken.py              # Kraken CCXT integration
│
├── trading/
│   ├── portfolio.py           # Portfolio and position tracking
│   ├── paper_trading.py       # Paper trading engine
│   ├── risk_manager.py        # Risk management and position sizing
│   ├── backtester.py          # Backtesting engine
│   └── metrics.py             # Performance metrics and reporting
│
├── strategies/
│   ├── base_strategy.py       # Base strategy class + indicators
│   └── strategies.py          # Concrete strategy implementations
│
└── utils/
    ├── config.py              # Configuration management
    └── logger.py              # Logging setup
```

## Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Live Paper Trading Example

```python
import asyncio
from src.exchanges.binance import BinanceExchange
from src.trading.portfolio import Portfolio
from src.trading.paper_trading import PaperTradingEngine
from src.trading.risk_manager import RiskManager

async def main():
    # Initialize
    exchange = BinanceExchange()
    portfolio = Portfolio(initial_balance=100)
    engine = PaperTradingEngine(exchange, portfolio)
    risk_manager = RiskManager(portfolio)
    
    # Get current price
    ticker = await exchange.get_ticker("BTC/USDT")
    price = ticker["last"]
    
    # Calculate position size
    stop_loss = price * 0.95
    pos_size = risk_manager.calculate_position_size(price, stop_loss)
    
    # Execute buy
    position = await engine.buy("BTC/USDT", pos_size, price, stop_loss=stop_loss)
    
    # View summary
    engine.print_portfolio_summary()
    
    await exchange.close()

asyncio.run(main())
```

### 3. Backtest a Strategy

```python
import asyncio
from src.trading.backtester import Backtester
from src.strategies.strategies import SMAcrossoverStrategy

async def strategy(index, exchange, engine):
    """Strategy logic"""
    strategy = SMAcrossoverStrategy()
    ohlcv = await exchange.get_ohlcv("BTC/USDT")
    closes = [c[4] for c in ohlcv]
    signal = await strategy.analyze({"closes": closes})
    
    if signal["action"] == "buy" and not engine.portfolio.positions:
        await engine.buy("BTC/USDT", 0.01)
    elif signal["action"] == "sell" and engine.portfolio.positions:
        for pos_id in list(engine.portfolio.positions.keys()):
            await engine.close(pos_id)

async def main():
    backtester = Backtester(initial_balance=100)
    
    # Load OHLCV data (sample data below)
    ohlcv_data = {"BTC/USDT": [...]}  # Historical candles
    
    results = await backtester.run_backtest(ohlcv_data, strategy)
    backtester.print_backtest_results(results)

asyncio.run(main())
```

### 4. Run Tests

```bash
pytest tests/ -v
pytest tests/test_portfolio.py -v  # Portfolio tests
pytest tests/test_risk_manager.py -v  # Risk management tests
pytest tests/test_strategies.py -v  # Strategy tests
```

## Core Components

### Portfolio
Manages paper trading account:
- Tracks cash and positions
- Calculates P&L (realized and unrealized)
- Maintains transaction history
- Generates performance statistics

```python
from src.trading.portfolio import Portfolio

portfolio = Portfolio(initial_balance=100)
position = portfolio.open_position("BTC/USDT", "buy", 0.01, 40000)
trade = portfolio.close_position(position.position_id, 45000)

stats = portfolio.get_stats()
# Returns: total_pnl, pnl_percentage, win_rate, etc.
```

### PaperTradingEngine
Executes simulated trades with market data:
- Fetches real prices from CCXT
- Applies slippage and fees
- Manages position open/close
- Monitors stop-loss and take-profit

```python
from src.trading.paper_trading import PaperTradingEngine

engine = PaperTradingEngine(exchange, portfolio, slippage=0.001, fee=0.001)

position = await engine.buy("BTC/USDT", amount=0.1, price=40000, stop_loss=38000)
trade = await engine.close(position.position_id, price=45000)

engine.print_portfolio_summary()
```

### RiskManager
Enforces trading risk limits:
- Calculates position sizes
- Validates trade parameters
- Tracks drawdown
- Implements Kelly Criterion

```python
from src.trading.risk_manager import RiskManager

risk_manager = RiskManager(portfolio, risk_per_trade=0.02, max_drawdown=0.2)

pos_size = risk_manager.calculate_position_size(40000, 38000)
validation = risk_manager.validate_trade(40000, 38000, pos_size)

if validation["valid"]:
    await engine.buy("BTC/USDT", pos_size)
```

### Backtester
Replays historical data for strategy testing:
- Loads OHLCV candles
- Simulates strategy execution
- Calculates performance metrics
- Generates detailed reports

```python
from src.trading.backtester import Backtester

backtester = Backtester(initial_balance=100)
results = await backtester.run_backtest(ohlcv_data, strategy_function)

backtester.print_backtest_results(results)
# Returns: return%, win_rate, sharpe_ratio, max_drawdown, etc.
```

### Strategies
Technical analysis strategies with indicators:

```python
from src.strategies.strategies import SMAcrossoverStrategy, RSIStrategy, MACDStrategy

# SMA Crossover
sma_strategy = SMAcrossoverStrategy(fast_period=10, slow_period=20)
signal = await sma_strategy.analyze({"closes": price_list})

# RSI Overbought/Oversold
rsi_strategy = RSIStrategy(rsi_period=14, overbought=70, oversold=30)
signal = await rsi_strategy.analyze({"closes": price_list})

# MACD Crossover
macd_strategy = MACDStrategy(fast=12, slow=26, signal=9)
signal = await macd_strategy.analyze({"closes": price_list})
```

## Performance Metrics

### Sharpe Ratio
Risk-adjusted return metric. Higher is better.
- Formula: (avg_return * 252 - risk_free_rate) / (std_dev * √252)
- Good: > 1.0, Excellent: > 2.0

### Sortino Ratio
Like Sharpe but only penalizes downside volatility.
- Better for strategies with asymmetric returns
- Good: > 1.0, Excellent: > 2.0

### Calmar Ratio
Return per unit of maximum drawdown.
- Formula: total_return / max_drawdown
- Good: > 0.5, Excellent: > 1.0

### Maximum Drawdown
Peak-to-trough decline during the backtest.
- Shows worst-case scenario
- Lower is better
- Typical: 10-30%

### Profit Factor
Ratio of gross wins to gross losses.
- Formula: total_wins / abs(total_losses)
- Good: > 1.5, Excellent: > 2.0

### Win Rate
Percentage of profitable trades.
- Formula: winning_trades / total_trades
- Good: > 50%, Excellent: > 60%

## Examples

### Example 1: Simple Buy & Hold
```python
async def hold_strategy(index, exchange, engine):
    if index == 0:  # First candle
        closes = await exchange.get_ohlcv("BTC/USDT")
        await engine.buy("BTC/USDT", 0.01, closes[-1]["close"])
```

### Example 2: DCA (Dollar Cost Averaging)
```python
async def dca_strategy(index, exchange, engine):
    if index % 24 == 0:  # Every 24 hours
        ticker = await exchange.get_ticker("BTC/USDT")
        await engine.buy("BTC/USDT", 0.001, ticker["last"])
```

### Example 3: Mean Reversion
```python
async def mean_reversion(index, exchange, engine):
    ohlcv = await exchange.get_ohlcv("BTC/USDT")
    closes = [c[4] for c in ohlcv]
    
    # Bollinger Bands
    bands = BaseStrategy.calculate_bollinger_bands(closes, 20, 2)
    current_price = closes[-1]
    
    if current_price < bands["lower"][-1]:
        await engine.buy("BTC/USDT", 0.01)
    elif current_price > bands["upper"][-1]:
        positions = list(engine.portfolio.positions.keys())
        if positions:
            await engine.close(positions[0])
```

## Data Requirements

For backtesting, you need OHLCV data in this format:

```python
ohlcv_data = {
    "BTC/USDT": [
        [timestamp, open, high, low, close, volume],
        [1673001600000, 40000, 40500, 39800, 40250, 100.5],
        ...
    ]
}
```

Where:
- `timestamp`: Unix milliseconds
- `open`, `high`, `low`, `close`: OHLC prices
- `volume`: Trading volume

## Limitations & Next Steps

### Current Limitations (Public APIs)
- ❌ Cannot place real trades (paper trading only)
- ❌ Cannot access account balances
- ❌ Cannot retrieve trading history
- ❌ No margin trading
- ❌ No leverage

### Next Steps for Live Trading
1. Add API credentials to `.env`
2. Replace exchange classes with authenticated versions
3. Implement actual order execution
4. Add portfolio sync with real exchange
5. Deploy to Railway/VPS

## Validation Checklist

- [x] Market data integration with public APIs
- [x] Paper trading simulation working
- [x] Risk management enforcing position limits
- [x] Portfolio tracking P&L accurately
- [x] Backtesting engine replaying historical data
- [x] Multiple strategies implemented
- [x] Performance metrics calculated (Sharpe, Sortino, Calmar)
- [x] Test suite passing
- [x] Ready for 7-day paper trading validation

## Next: Transition to Live Trading

Once paper trading is validated:

1. **Add API Credentials**: Update `.env` with exchange credentials
2. **Implement Authenticated Endpoints**: Create live exchange classes
3. **Dual-Mode System**: Support both paper and live modes
4. **Deployment**: Deploy to Railway with monitoring

For detailed setup, see [build.md](../build.md)

## License

MIT
