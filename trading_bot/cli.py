#!/usr/bin/env python3
"""
CLI entry point for placing orders on Binance Futures testnet.
Supports live trading and dry-run (demo) mode.
"""

import argparse
import sys
import io

# Fix Windows console encoding for Unicode output
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if sys.stderr.encoding != 'utf-8':
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import logging
from typing import Optional

from bot.client import BinanceFuturesClient
from bot.orders import OrderManager
from bot.validators import (
    validate_symbol,
    validate_side,
    validate_order_type,
    validate_quantity,
    validate_price,
    validate_stop_price,
)
from bot.logging_config import setup_logging

# Initialize logging
setup_logging()
logger = logging.getLogger(__name__)


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returns:
        Parsed arguments namespace.
    """
    parser = argparse.ArgumentParser(
        description="Place orders on Binance Futures Testnet (USDT-M).",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry-run mode (no API keys needed):
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01 --dry-run

  # Live testnet orders:
  python cli.py --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
  python cli.py --symbol BTCUSDT --side SELL --type LIMIT --quantity 0.01 --price 30000
  python cli.py --symbol ETHUSDT --side BUY --type STOP_LIMIT --quantity 0.1 --price 2000 --stop_price 1950
        """
    )

    parser.add_argument(
        "--symbol",
        required=True,
        help="Trading pair symbol (e.g., BTCUSDT)"
    )
    parser.add_argument(
        "--side",
        required=True,
        choices=["BUY", "SELL"],
        help="Order side: BUY or SELL"
    )
    parser.add_argument(
        "--type",
        required=True,
        dest="order_type",
        choices=["MARKET", "LIMIT", "STOP_LIMIT"],
        help="Order type: MARKET, LIMIT, or STOP_LIMIT"
    )
    parser.add_argument(
        "--quantity",
        required=True,
        help="Order quantity (e.g., 0.01)"
    )
    parser.add_argument(
        "--price",
        help="Limit price (required for LIMIT and STOP_LIMIT orders)"
    )
    parser.add_argument(
        "--stop_price",
        help="Stop trigger price (required for STOP_LIMIT orders)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=False,
        dest="dry_run",
        help="Run in dry-run mode (simulate orders without API keys)"
    )

    return parser.parse_args()


def validate_inputs(args: argparse.Namespace) -> tuple:
    """
    Validate all inputs and return processed values.

    Args:
        args: Parsed arguments.

    Returns:
        Tuple of (valid, error_message, validated_data).
    """
    errors = []
    validated = {}

    # Validate symbol
    valid, err = validate_symbol(args.symbol)
    if not valid:
        errors.append(err)
    validated["symbol"] = args.symbol.upper()

    # Validate side (already limited by choices, but double-check)
    valid, err = validate_side(args.side)
    if not valid:
        errors.append(err)
    validated["side"] = args.side.upper()

    # Validate order type
    valid, err = validate_order_type(args.order_type)
    if not valid:
        errors.append(err)
    validated["order_type"] = args.order_type.upper()

    # Validate quantity
    valid, err, qty = validate_quantity(args.quantity)
    if not valid:
        errors.append(err)
    else:
        validated["quantity"] = qty

    # Validate price based on order type
    valid, err, price = validate_price(args.price, args.order_type)
    if not valid:
        errors.append(err)
    validated["price"] = price

    # Validate stop price for STOP_LIMIT
    valid, err, stop_price = validate_stop_price(args.stop_price, args.order_type)
    if not valid:
        errors.append(err)
    validated["stop_price"] = stop_price

    if errors:
        return False, "\n".join(errors), None

    return True, None, validated


def print_order_summary(validated_data: dict, dry_run: bool = False) -> None:
    """
    Print a summary of the order request.

    Args:
        validated_data: Dictionary with validated order parameters.
        dry_run: Whether this is a dry-run.
    """
    mode = "🔧 DRY-RUN" if dry_run else "🔴 LIVE TESTNET"
    print(f"\n{'='*50}")
    print(f"  Mode: {mode}")
    print(f"  Placing {validated_data['order_type']} order...")
    print(f"  Symbol:   {validated_data['symbol']}")
    print(f"  Side:     {validated_data['side']}")
    print(f"  Quantity: {validated_data['quantity']}")
    if validated_data.get("price") is not None:
        print(f"  Price:    {validated_data['price']}")
    if validated_data.get("stop_price") is not None:
        print(f"  Stop:     {validated_data['stop_price']}")
    print(f"{'='*50}")


def print_order_response(response: dict, dry_run: bool = False) -> None:
    """
    Print formatted order response.

    Args:
        response: Order response dictionary.
        dry_run: Whether this is a dry-run.
    """
    print("\n📋 Order Response:")
    print("-" * 40)
    print(f"  Order ID:      {response.get('orderId')}")
    print(f"  Status:        {response.get('status')}")
    print(f"  Symbol:        {response.get('symbol')}")
    print(f"  Side:          {response.get('side')}")
    print(f"  Type:          {response.get('type')}")
    print(f"  Quantity:      {response.get('executedQty') or response.get('origQty')}")
    print(f"  Avg Price:     {response.get('avgPrice')}")
    if response.get("stopPrice"):
        print(f"  Stop Price:    {response.get('stopPrice')}")
    if response.get("note"):
        print(f"  ⚠️  Note:      {response.get('note')}")
    print("-" * 40)

    if dry_run:
        print("🔧 DRY-RUN: Order simulated successfully (no real order placed)\n")
    else:
        print("✅ Order placed successfully on Binance Futures Testnet\n")


def main() -> None:
    """Main CLI entry point."""
    args = parse_arguments()
    dry_run = args.dry_run

    # Validate inputs
    is_valid, error_msg, validated_data = validate_inputs(args)
    if not is_valid:
        logger.error(f"Input validation failed:\n{error_msg}")
        print("\n❌ Validation Error:")
        print(error_msg)
        sys.exit(1)

    # Initialize client and order manager
    try:
        client_wrapper = BinanceFuturesClient(dry_run=dry_run)
        # Test connection (optional but good practice)
        if not client_wrapper.test_connection():
            print("❌ Could not connect to Binance Futures testnet. Check your network and API keys.")
            print("💡 Tip: Use --dry-run to test without API keys.")
            sys.exit(1)
        order_manager = OrderManager(client_wrapper)
    except Exception as e:
        logger.error(f"Failed to initialize client: {e}")
        print(f"\n❌ Initialization Error: {e}")
        sys.exit(1)

    # Print order summary
    print_order_summary(validated_data, dry_run)

    # Place order based on type
    try:
        if validated_data["order_type"] == "MARKET":
            response = order_manager.place_market_order(
                symbol=validated_data["symbol"],
                side=validated_data["side"],
                quantity=validated_data["quantity"]
            )
        elif validated_data["order_type"] == "LIMIT":
            response = order_manager.place_limit_order(
                symbol=validated_data["symbol"],
                side=validated_data["side"],
                quantity=validated_data["quantity"],
                price=validated_data["price"]
            )
        elif validated_data["order_type"] == "STOP_LIMIT":
            response = order_manager.place_stop_limit_order(
                symbol=validated_data["symbol"],
                side=validated_data["side"],
                quantity=validated_data["quantity"],
                price=validated_data["price"],
                stop_price=validated_data["stop_price"]
            )
        else:
            raise ValueError(f"Unsupported order type: {validated_data['order_type']}")

        print_order_response(response, dry_run)

    except Exception as e:
        logger.error(f"Order placement failed: {e}")
        print(f"\n❌ Order failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
