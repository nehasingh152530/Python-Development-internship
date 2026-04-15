"""Order placement logic for Binance Futures."""

import logging
import json
from datetime import datetime
from typing import Dict, Any, Optional

from binance.exceptions import BinanceAPIException, BinanceRequestException

from bot.client import BinanceFuturesClient

logger = logging.getLogger(__name__)


class OrderManager:
    """
    Manages order placement on Binance Futures testnet.
    Supports both live and dry-run modes.
    """

    def __init__(self, client_wrapper: BinanceFuturesClient):
        """
        Initialize with a BinanceFuturesClient instance.

        Args:
            client_wrapper: Configured BinanceFuturesClient.
        """
        self.client_wrapper = client_wrapper
        self.dry_run = client_wrapper.is_dry_run()
        self.client = client_wrapper.get_client()

    def _generate_dry_run_response(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Generate a simulated order response for dry-run mode.

        Args:
            symbol: Trading pair.
            side: BUY or SELL.
            order_type: MARKET, LIMIT, or STOP.
            quantity: Order quantity.
            price: Limit price (optional).
            stop_price: Stop price (optional).

        Returns:
            Simulated order response dictionary.
        """
        simulated_price = price or 50000.00  # Default simulated price for MARKET
        return {
            "orderId": f"DRY-RUN-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "symbol": symbol,
            "status": "SIMULATED",
            "executedQty": str(quantity),
            "avgPrice": str(simulated_price),
            "type": order_type,
            "side": side,
            "price": str(price) if price else "MARKET",
            "origQty": str(quantity),
            "stopPrice": str(stop_price) if stop_price else None,
            "note": "This is a DRY-RUN simulation. No real order was placed."
        }

    def place_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float
    ) -> Dict[str, Any]:
        """
        Place a MARKET order on Binance Futures testnet.

        Args:
            symbol: Trading pair (e.g., BTCUSDT).
            side: 'BUY' or 'SELL'.
            quantity: Order quantity.

        Returns:
            Dictionary containing order response details.
        """
        logger.info(f"Placing MARKET order: {symbol} {side} Qty={quantity}")

        if self.dry_run:
            logger.info("🔧 DRY-RUN: Simulating MARKET order.")
            return self._generate_dry_run_response(symbol, side, "MARKET", quantity)

        try:
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type="MARKET",
                quantity=quantity
            )
            logger.info(f"MARKET order placed successfully: {order}")
            return self._format_order_response(order)
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Binance API error placing MARKET order: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error placing MARKET order: {e}")
            raise

    def place_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Place a LIMIT order on Binance Futures testnet.

        Args:
            symbol: Trading pair (e.g., BTCUSDT).
            side: 'BUY' or 'SELL'.
            quantity: Order quantity.
            price: Limit price.
            time_in_force: Time in force policy (default GTC).

        Returns:
            Dictionary containing order response details.
        """
        logger.info(f"Placing LIMIT order: {symbol} {side} Qty={quantity} Price={price} TIF={time_in_force}")

        if self.dry_run:
            logger.info("🔧 DRY-RUN: Simulating LIMIT order.")
            return self._generate_dry_run_response(symbol, side, "LIMIT", quantity, price)

        try:
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type="LIMIT",
                quantity=quantity,
                price=str(price),  # ensure string for precision
                timeInForce=time_in_force
            )
            logger.info(f"LIMIT order placed successfully: {order}")
            return self._format_order_response(order)
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Binance API error placing LIMIT order: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error placing LIMIT order: {e}")
            raise

    def place_stop_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        time_in_force: str = "GTC"
    ) -> Dict[str, Any]:
        """
        Place a STOP-LIMIT order on Binance Futures testnet.

        Args:
            symbol: Trading pair.
            side: 'BUY' or 'SELL'.
            quantity: Order quantity.
            price: Limit price once triggered.
            stop_price: Trigger price.
            time_in_force: Time in force.

        Returns:
            Dictionary containing order response details.
        """
        logger.info(
            f"Placing STOP-LIMIT order: {symbol} {side} Qty={quantity} "
            f"Price={price} StopPrice={stop_price} TIF={time_in_force}"
        )

        if self.dry_run:
            logger.info("🔧 DRY-RUN: Simulating STOP-LIMIT order.")
            return self._generate_dry_run_response(symbol, side, "STOP", quantity, price, stop_price)

        try:
            order = self.client.futures_create_order(
                symbol=symbol.upper(),
                side=side.upper(),
                type="STOP",
                quantity=quantity,
                price=str(price),
                stopPrice=str(stop_price),
                timeInForce=time_in_force
            )
            logger.info(f"STOP-LIMIT order placed successfully: {order}")
            return self._format_order_response(order)
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Binance API error placing STOP-LIMIT order: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error placing STOP-LIMIT order: {e}")
            raise

    def _format_order_response(self, order: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract and format relevant fields from the order response.

        Args:
            order: Raw order response from Binance.

        Returns:
            Formatted dictionary with key order details.
        """
        # Handle different response structures (e.g., MARKET vs LIMIT)
        avg_price = order.get("avgPrice", "0.0")
        if avg_price is None or avg_price == "0.0":
            avg_price = "N/A"

        return {
            "orderId": order.get("orderId"),
            "symbol": order.get("symbol"),
            "status": order.get("status"),
            "executedQty": order.get("executedQty"),
            "avgPrice": avg_price,
            "type": order.get("type"),
            "side": order.get("side"),
            "price": order.get("price"),
            "origQty": order.get("origQty"),
        }
