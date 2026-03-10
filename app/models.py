from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class Tick:
    ts: datetime
    price: float


@dataclass
class Position:
    qty: float = 0.0
    avg_price: float = 0.0


@dataclass
class BotState:
    mode: str = "paper"
    last_price: float = 0.0
    moving_avg: float = 0.0
    zscore: float = 0.0
    signal: str = "HOLD"
    position_qty: float = 0.0
    unrealized_pnl: float = 0.0
    realized_pnl: float = 0.0
    equity: float = 10000.0
    last_error: str = ""
    last_update: str = ""

    def to_dict(self):
        return asdict(self)
