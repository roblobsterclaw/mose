#!/usr/bin/env python3
"""Brokerage adapter contracts for MOSE.

All brokerage integrations start read-only. Trading methods are intentionally
absent until MOSE has explicit risk controls, confirmations, and audit trails.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class BrokerageAccount:
    account_id: str
    name: str
    brokerage: str
    account_type: str | None = None


@dataclass(frozen=True)
class BrokeragePosition:
    account_id: str
    ticker: str
    shares: float
    cost_basis_per_share: float | None
    market_price: float | None
    currency: str = "USD"
    broker_position_id: str | None = None


@dataclass(frozen=True)
class BrokerageTrade:
    account_id: str
    ticker: str
    side: str
    shares: float
    price: float | None
    traded_at: str
    broker_trade_id: str | None = None


class BrokerageAdapter(Protocol):
    """Read-only brokerage sync surface."""

    name: str

    def list_accounts(self) -> list[BrokerageAccount]:
        """Return accounts available to sync."""

    def list_positions(self, account_id: str) -> list[BrokeragePosition]:
        """Return open positions for an account."""

    def list_recent_trades(self, account_id: str) -> list[BrokerageTrade]:
        """Return recent executed trades for audit and cost-basis tracking."""
