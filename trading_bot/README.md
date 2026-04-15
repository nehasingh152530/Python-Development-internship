# Binance Futures Testnet Trading Bot

A production-ready Python CLI application for placing orders on Binance Futures Testnet (USDT-M).

## Features

- Place **MARKET**, **LIMIT**, and **STOP-LIMIT** orders on Binance Futures Testnet.
- **Dry-run mode** — Simulate orders without API keys for testing/demonstration.
- Input validation with helpful error messages.
- Structured logging to file (`bot.log`) and console.
- Clean, modular codebase with separation of concerns.
- `.env` file support for secure API key management.
- Uses Binance Futures Testnet – no real funds required.

## Project Structure

```
trading_bot/
├── cli.py              # CLI entry point
├── bot/
│   ├── __init__.py     # Package init
│   ├── client.py       # Binance API client wrapper
│   ├── orders.py       # Order placement logic
│   ├── validators.py   # Input validation
│   └── logging_config.py  # Logging setup
├── requirements.txt    # Dependencies
├── .env.example        # Example environment config
└── README.md           # This file
```

## Prerequisites

- Python 3.7 or higher
- Binance account (for testnet API keys) — *optional for dry-run mode*

## Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. API Keys (Optional for dry-run)

**Option A: Using `.env` file (recommended)**
```bash
cp .env.example .env
# Edit .env with your testnet API keys
```

**Option B: Environment variables**

Linux/Mac:
```bash
export BINANCE_API_KEY='your_testnet_api_key'
export BINANCE_SECRET_KEY='your_testnet_api_secret'
```

Windows (PowerShell):
```powershell
$env:BINANCE_API_KEY="your_testnet_api_key"
$env:BINANCE_SECRET_KEY="your_testnet_api_secret"
```

Get your testnet keys from: https://testnet.binancefuture.com/

## Usage

### Dry-Run Mode (No API Keys Required)

Test the bot without connecting to Binance:

```bash
# Market order simulation
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01 --dry-run

# Limit order simulation
python cli.py --symbol ETHUSDT --side SELL --type LIMIT --quantity 0.5 --price 3000 --dry-run

# Stop-limit order simulation
python cli.py --symbol BTCUSDT --side BUY --type STOP_LIMIT --quantity 0.01 --price 60000 --stop_price 59000 --dry-run
```

### Live Testnet Trading

```bash
# Place a market order
python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01

# Place a limit order
python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 60000

# Place a stop-limit order
python cli.py --symbol ETHUSDT --side BUY --type STOP_LIMIT --quantity 0.1 --price 2000 --stop_price 1950
```

### Help

```bash
python cli.py --help
```

## Order Types

| Type | Description | Required Args |
|------|-------------|---------------|
| MARKET | Execute immediately at market price | `--symbol`, `--side`, `--quantity` |
| LIMIT | Execute at specified price or better | `--symbol`, `--side`, `--quantity`, `--price` |
| STOP_LIMIT | Trigger at stop price, then place limit | `--symbol`, `--side`, `--quantity`, `--price`, `--stop_price` |

## Logging

All operations are logged to `bot.log` with timestamps. Console output shows user-friendly messages.

## Architecture

- **`cli.py`**: Handles argument parsing, validation orchestration, and output formatting.
- **`bot/client.py`**: Manages Binance API connection with testnet configuration and dry-run support.
- **`bot/orders.py`**: Implements order placement logic for all three order types with error handling.
- **`bot/validators.py`**: Validates all input parameters (symbol, side, quantity, price, etc.).
- **`bot/logging_config.py`**: Configures dual logging (file + console).
