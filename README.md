# Cryptocurrency Trading Bot

A Python-based trading bot for automated cryptocurrency trading with support for multiple exchanges and trading modes.

## Features

- **Multi-Exchange Support**: Binance, Coinbase, Kraken
- **Multiple Trading Modes**: Paper trading, Backtesting, Live trading
- **Risk Management**: Built-in risk protocols and position sizing
- **Async Operations**: Asynchronous API calls for better performance
- **Logging**: Comprehensive logging across all environments
- **Infrastructure as Code**: Railway deployment ready

## Quick Start

### Prerequisites

- Python 3.8+
- pip package manager
- Git

### Installation

1. Clone the repository:
```bash
git clone https://github.com/rasta-pasta-710/Trade-bot.git
cd Trade-bot
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Setup environment:
```bash
cp .env.example .env
# Edit .env with your API credentials
```

### Usage

**Paper Trading (7-day validation):**
```bash
python bot.py --mode=paper --exchange=binance
```

**Backtesting:**
```bash
python bot.py --mode=backtest --exchange=binance
```

**Live Trading:**
```bash
python bot.py --mode=live --exchange=binance
```

## Project Structure

```
Trade-bot/
├── src/
│   ├── exchanges/          # Exchange integrations
│   ├── strategies/         # Trading strategies
│   ├── trading/            # Main bot logic
│   └── utils/              # Utilities (config, logging)
├── tests/                  # Test suite
├── config/                 # Configuration files
├── bot.py                  # Entry point
├── requirements.txt        # Dependencies
└── .env.example           # Environment template
```

## Configuration

All configuration is managed via `.env` file. See `.env.example` for available options.

### API Credentials

- **Binance**: `BINANCE_API_KEY`, `BINANCE_API_SECRET`
- **Coinbase**: `COINBASE_API_KEY`, `COINBASE_API_SECRET`, `COINBASE_PASSPHRASE`
- **Kraken**: `KRAKEN_API_KEY`, `KRAKEN_API_SECRET`

## Testing

Run the test suite:
```bash
pytest tests/ -v
```

## Deployment

### Railway

```bash
railway link
railway up
```

### Windows VPS

Configure secondary instance with same `.env` file for failover support.

## Validation Checklist

- [ ] Paper trading shows positive returns
- [ ] Risk management tests pass
- [ ] Logging configured on both environments
- [ ] Failover tested and working
- [ ] Ready for $100 live deployment

## License

MIT

## Support

For issues or questions, please open an issue on GitHub.
