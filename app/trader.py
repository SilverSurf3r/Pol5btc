from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Fill:
    side: str
    qty: float
    price: float


class PaperTrader:
    def __init__(self, order_size_usd: float, max_position_usd: float):
        self.order_size_usd = order_size_usd
        self.max_position_usd = max_position_usd
        self.qty = 0.0
        self.avg_price = 0.0
        self.realized_pnl = 0.0

    def execute(self, signal: str, price: float) -> Fill | None:
        if signal not in {"BUY", "SELL"} or price <= 0:
            return None

        target_qty = self.order_size_usd / price
        notional = abs(self.qty * price)
        if signal == "BUY" and notional >= self.max_position_usd:
            return None
        if signal == "SELL" and self.qty <= 0:
            return None

        if signal == "BUY":
            new_qty = self.qty + target_qty
            self.avg_price = ((self.avg_price * self.qty) + (price * target_qty)) / new_qty if new_qty else 0.0
            self.qty = new_qty
        else:  # SELL
            sell_qty = min(target_qty, self.qty)
            self.realized_pnl += (price - self.avg_price) * sell_qty
            self.qty -= sell_qty
            if self.qty == 0:
                self.avg_price = 0.0
            target_qty = sell_qty

        return Fill(side=signal, qty=target_qty, price=price)

    def unrealized(self, price: float) -> float:
        if self.qty <= 0:
            return 0.0
        return (price - self.avg_price) * self.qty
