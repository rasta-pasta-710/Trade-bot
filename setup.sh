#!/usr/bin/env bash

# Paper Trading Quick Start Guide
# Run this script to get started with paper trading

echo "==================================================="
echo "  Cryptocurrency Trading Bot - Paper Trading"
echo "==================================================="
echo ""

# Check Python
echo "✓ Checking Python version..."
python3 --version

echo ""
echo "✓ Installing dependencies..."
pip install -r requirements.txt -q

echo ""
echo "✓ Project Structure:"
echo "  src/                   - Core source code"
echo "  src/exchanges/         - CCXT exchange integrations"
echo "  src/trading/           - Trading engine & portfolio"
echo "  src/strategies/        - Trading strategies"
echo "  tests/                 - Test suite"
echo "  examples/              - Usage examples"
echo ""

echo "✓ Running tests..."
pytest tests/ -v --tb=short

echo ""
echo "==================================================="
echo "  READY FOR PAPER TRADING! 🚀"
echo "==================================================="
echo ""
echo "Quick commands:"
echo "  Live Paper Trading:  python examples/live_paper_trading.py"
echo "  Backtest Strategy:   python examples/backtest_sma.py"
echo "  Run All Tests:       pytest tests/ -v"
echo ""
echo "Documentation:"
echo "  - PAPER_TRADING.md        - Complete usage guide"
echo "  - COMPLETION_SUMMARY.md   - What's built"
echo "  - README.md               - Project overview"
echo ""
echo "Next steps:"
echo "  1. Review PAPER_TRADING.md"
echo "  2. Run: python examples/live_paper_trading.py"
echo "  3. Run: python examples/backtest_sma.py"
echo ""
