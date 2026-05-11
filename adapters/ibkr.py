#!/usr/bin/env python3
"""IBKR adapter placeholder.

IBKR should be connected only after local portfolio syncing is stable. The first
implementation should read accounts, positions, and recent trades through either
TWS API / IB Gateway or the Client Portal Web API. No order placement belongs in
this adapter yet.
"""

from __future__ import annotations

from adapters.brokerage import BrokerageAccount, BrokeragePosition, BrokerageTrade


class IBKRReadOnlyAdapter:
    name = "IBKR"

    def __init__(self, host: str = "127.0.0.1", port: int | None = None) -> None:
        self.host = host
        self.port = port

    def list_accounts(self) -> list[BrokerageAccount]:
        raise NotImplementedError("IBKR account sync is planned after SQLite portfolio lots are stable.")

    def list_positions(self, account_id: str) -> list[BrokeragePosition]:
        raise NotImplementedError("IBKR position sync is planned after SQLite portfolio lots are stable.")

    def list_recent_trades(self, account_id: str) -> list[BrokerageTrade]:
        raise NotImplementedError("IBKR trade sync is planned after SQLite portfolio lots are stable.")
