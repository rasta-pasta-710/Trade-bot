
# Exchanges

## Supported Platforms

### Centralized Exchanges (CEX)
| Exchange | API Support | Features | Status |
|----------|-------------|----------|--------|
| Binance | REST, WebSocket | Spot, Futures, Margin | Active |
| Coinbase | REST | Spot Trading | Active |
| Kraken | REST | Spot, Futures | Active |

### Exchange Configuration

```json
{
    "exchanges": [
        {
            "name": "binance",
            "type": "cex",
            "endpoints": {
                "rest": "https://api.binance.com",
                "ws": "wss://stream.binance.com:9443"
            },
            "auth_required": true,
            "rate_limit": 1200
        }
    ]
}
```

## API Integration

### Connection Pattern
```python
def get_exchange(platform: str):
        """Factory pattern for exchange instantiation"""
        # Returns configured exchange instance
```

### Required Credentials
- `API_KEY`
- `API_SECRET`
- `PASSPHRASE` (if applicable)

## Data Points

### Market Data
- Real-time price feeds
- Order book depth
- Trading volume
- Historical OHLCV candles

### Account Data
- Portfolio balance
- Open positions
- Trading history
- Fee structure
