from __future__ import annotations

import random
from datetime import datetime, timezone

import httpx


class PolymarketClient:
    """Fetch token price from Polymarket Gamma API with resilient fallback."""

    def __init__(self, market_slug: str):
        self.market_slug = market_slug
        self.gamma_url = f"https://gamma-api.polymarket.com/markets?slug={market_slug}"
        self._fallback = 0.5

    def _next_fallback(self) -> tuple[float, datetime]:
        self._fallback = max(0.01, min(0.99, self._fallback + random.uniform(-0.01, 0.01)))
        return self._fallback, datetime.now(timezone.utc)

    async def get_price(self) -> tuple[float, datetime]:
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(self.gamma_url)
                resp.raise_for_status()
                payload = resp.json()
                if payload and isinstance(payload, list):
                    market = payload[0]
                    price = market.get("lastTradePrice") or market.get("bestBid") or market.get("bestAsk")
                    if price is not None:
                        self._fallback = float(price)
                        return float(price), datetime.now(timezone.utc)
        except Exception:
            return self._next_fallback()

        return self._next_fallback()
