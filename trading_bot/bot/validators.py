"""Input validation functions for order placement."""

import re
from typing import Optional, Tuple


def validate_symbol(symbol: str) -> Tuple[bool, Optional[str]]:
    """
    Validate the trading symbol format.

    Args:
        symbol: Trading pair symbol (e.g., BTCUSDT or btcusdt).

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not symbol or not isinstance(symbol, str):
        return False, "Symbol must be a non-empty string."

    # Normalize to uppercase for validation
    symbol_upper = symbol.upper().strip()

    # Basic pattern: uppercase letters, optionally with numbers, typically ending with USDT
    pattern = r"^[A-Z0-9]{2,20}$"
    if not re.match(pattern, symbol_upper):
        return False, f"Symbol '{symbol}' is invalid. Must be alphanumeric (e.g., BTCUSDT)."

    return True, None


def validate_side(side: str) -> Tuple[bool, Optional[str]]:
    """
    Validate order side.

    Args:
        side: 'BUY' or 'SELL' (case-insensitive).

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not side or not isinstance(side, str):
        return False, "Side must be a non-empty string."

    side_upper = side.upper().strip()
    if side_upper not in ("BUY", "SELL"):
        return False, "Side must be either 'BUY' or 'SELL'."

    return True, None


def validate_order_type(order_type: str) -> Tuple[bool, Optional[str]]:
    """
    Validate order type.

    Args:
        order_type: 'MARKET', 'LIMIT', or 'STOP_LIMIT' (case-insensitive).

    Returns:
        Tuple of (is_valid, error_message).
    """
    if not order_type or not isinstance(order_type, str):
        return False, "Order type must be a non-empty string."

    type_upper = order_type.upper().strip()
    valid_types = ("MARKET", "LIMIT", "STOP_LIMIT")
    if type_upper not in valid_types:
        return False, f"Order type must be one of: {', '.join(valid_types)}."

    return True, None


def validate_quantity(quantity: str) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Validate order quantity.

    Args:
        quantity: String representation of quantity.

    Returns:
        Tuple of (is_valid, error_message, float_value).
    """
    if not quantity:
        return False, "Quantity is required.", None

    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        return False, f"Quantity '{quantity}' must be a valid number.", None

    if qty <= 0:
        return False, "Quantity must be greater than 0.", None

    if qty > 1000000:
        return False, "Quantity seems unreasonably large. Max allowed: 1,000,000.", None

    return True, None, qty


def validate_price(price: Optional[str], order_type: str) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Validate price parameter.

    Args:
        price: String representation of price (optional).
        order_type: Order type to determine if price is required.

    Returns:
        Tuple of (is_valid, error_message, float_value).
    """
    type_upper = order_type.upper().strip()
    if type_upper in ("LIMIT", "STOP_LIMIT"):
        if not price:
            return False, f"Price is required for {order_type} orders.", None
        try:
            p = float(price)
        except (ValueError, TypeError):
            return False, f"Price '{price}' must be a valid number.", None
        if p <= 0:
            return False, "Price must be greater than 0.", None
        return True, None, p
    else:
        # MARKET orders do not require price
        if price is not None:
            pass  # Ignore price for MARKET orders
        return True, None, None


def validate_stop_price(stop_price: Optional[str], order_type: str) -> Tuple[bool, Optional[str], Optional[float]]:
    """
    Validate stopPrice parameter for STOP_LIMIT orders.

    Args:
        stop_price: String representation of stop price.
        order_type: Order type.

    Returns:
        Tuple of (is_valid, error_message, float_value).
    """
    if order_type.upper().strip() == "STOP_LIMIT":
        if not stop_price:
            return False, "stopPrice is required for STOP_LIMIT orders.", None
        try:
            sp = float(stop_price)
        except (ValueError, TypeError):
            return False, f"Stop price '{stop_price}' must be a valid number.", None
        if sp <= 0:
            return False, "Stop price must be greater than 0.", None
        return True, None, sp
    else:
        return True, None, None
