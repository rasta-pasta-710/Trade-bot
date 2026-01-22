
# Build Guide

## Prerequisites
- Python 3.8+
- pip package manager
- Git
- Railway CLI (for deployment)
- API credentials for supported platforms

## Setup

### 1. Clone & Install
```bash
git clone https://github.com/rasta-pasta-710/Trade-bot.git
cd Trade-bot
pip install -r requirements.txt
```

### 2. Configure Environment
Create `.env` file with:
```
PLATFORM_API_KEY=your_key
AI_API_KEY=your_key
ENVIRONMENT=development
```

### 3. Paper Trading
```bash
python bot.py --mode=paper --duration=7d
```

## Deployment

### Local Testing
```bash
python bot.py --mode=backtest
```

### Railway Deployment
```bash
railway link
railway up
```

### Windows VPS Backup
- Configure secondary instance with same `.env`
- Set failover monitoring for redundancy

## Validation Checklist
- [ ] Paper trading shows positive returns
- [ ] Risk management tests pass
- [ ] Logging configured on both environments
- [ ] Failover tested and working
- [ ] Ready for $100 live deployment
