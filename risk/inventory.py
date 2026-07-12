"""
inventory.py

InventoryLimitRule: rejects an order if EXECUTING it would push the
firm's position in that symbol beyond a configured maximum absolute
inventory. STATEFUL -- tracks a running position per symbol across
every order that's been accepted.

SIMPLIFICATION: inventory updates when an order is ACCEPTED, modeling
an instant fill. A real system updates on actual FILL confirmations.
"""
from __future__ import annotations

from .order import Order, Side
from .price_collar import RuleResult


class InventoryTracker:
    def __init__(self):
        self._positions: dict = {}

    def position(self, symbol: str) -> float:
        return self._positions.get(symbol, 0.0)

    def apply_fill(self, order: Order) -> None:
        delta = order.quantity if order.side == Side.BUY else -order.quantity
        self._positions[order.symbol] = self.position(order.symbol) + delta


class InventoryLimitRule:
    def __init__(self, config: dict, tracker: InventoryTracker):
        self.config = config
        self.tracker = tracker

    def _max_inventory_for(self, symbol: str) -> float:
        symbol_config = self.config.get(symbol)
        if symbol_config is None:
            raise KeyError(
                f"no risk config found for symbol '{symbol}' -- refusing to "
                f"guess a default inventory limit; add it to config.json"
            )
        return symbol_config["max_inventory"]

    def check(self, order: Order, current_price: float) -> RuleResult:
        max_inventory = self._max_inventory_for(order.symbol)
        current_position = self.tracker.position(order.symbol)
        delta = order.quantity if order.side == Side.BUY else -order.quantity
        proposed_position = current_position + delta

        details = {
            "current_position": current_position,
            "proposed_position": proposed_position,
            "max_inventory": max_inventory,
        }

        if abs(proposed_position) <= max_inventory:
            return RuleResult(True, "within inventory limit", details)
        return RuleResult(
            False,
            f"executing this order would move position from {current_position} to "
            f"{proposed_position}, exceeding max inventory of {max_inventory}",
            details,
        )
