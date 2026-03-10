from __future__ import annotations
from collections import deque
from statistics import mean, pstdev


class MeanReversionStrategy:
    def __init__(self, window: int, z_threshold: float):
        self.window = window
        self.z_threshold = z_threshold
        self.prices = deque(maxlen=window)

    def on_price(self, price: float) -> dict:
        self.prices.append(price)
        ma = mean(self.prices)
        sd = pstdev(self.prices) if len(self.prices) > 1 else 0.0
        z = (price - ma) / sd if sd > 0 else 0.0

        signal = "HOLD"
        if len(self.prices) >= self.window:
            if z >= self.z_threshold:
                signal = "SELL"
            elif z <= -self.z_threshold:
                signal = "BUY"

        return {"moving_avg": ma, "zscore": z, "signal": signal}
