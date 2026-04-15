"""Binance Futures testnet client wrapper."""

import os
import logging
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()  # Load .env file if present
except ImportError:
    pass  # python-dotenv not installed, environment variables must be set manually

from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceRequestException

logger = logging.getLogger(__name__)


class BinanceFuturesClient:
    """
    Wrapper for Binance Futures testnet client.
    Handles connection, authentication, and error handling.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        testnet: bool = True,
        dry_run: bool = False
    ):
        """
        Initialize the Binance Futures testnet client.

        Args:
            api_key: Binance API key. If None, reads from BINANCE_API_KEY env var.
            api_secret: Binance API secret. If None, reads from BINANCE_SECRET_KEY env var.
            testnet: Always True for testnet usage.
            dry_run: If True, skip actual API connection (for demo/testing).
        """
        self.dry_run = dry_run
        self.testnet = testnet
        self.client: Optional[Client] = None

        if dry_run:
            logger.info("🔧 DRY-RUN mode: No actual API connection will be made.")
            return

        self.api_key = api_key or os.getenv("BINANCE_API_KEY")
        self.api_secret = api_secret or os.getenv("BINANCE_SECRET_KEY")

        if not self.api_key or not self.api_secret:
            raise ValueError(
                "API key and secret are required. Set BINANCE_API_KEY and "
                "BINANCE_SECRET_KEY environment variables, create a .env file, "
                "or pass them explicitly.\n"
                "Tip: Use --dry-run to test without API keys."
            )

        self._initialize_client()

    def _initialize_client(self) -> None:
        """
        Initialize the Binance client with Futures testnet configuration.
        """
        try:
            self.client = Client(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=self.testnet
            )
            # Override the Futures URL to ensure testnet is used
            self.client.FUTURES_URL = "https://testnet.binancefuture.com"
            logger.info("✅ Binance Futures testnet client initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize Binance client: {e}")
            raise

    def test_connection(self) -> bool:
        """
        Test the connection to Binance Futures testnet.

        Returns:
            True if connection is successful (or in dry-run mode), False otherwise.
        """
        if self.dry_run:
            logger.info("🔧 DRY-RUN: Skipping connection test.")
            return True

        try:
            self.client.futures_ping()
            logger.info("✅ Connection test successful.")
            return True
        except (BinanceAPIException, BinanceRequestException) as e:
            logger.error(f"Connection test failed: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during connection test: {e}")
            return False

    def get_client(self) -> Optional[Client]:
        """
        Get the underlying Binance client instance.

        Returns:
            The Binance Client object, or None in dry-run mode.
        """
        if self.dry_run:
            return None
        if self.client is None:
            self._initialize_client()
        return self.client

    def is_dry_run(self) -> bool:
        """Check if client is in dry-run mode."""
        return self.dry_run
