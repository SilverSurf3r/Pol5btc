from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()


class Settings(BaseModel):
    market_slug: str = os.getenv("POLYMARKET_MARKET_SLUG", "will-bitcoin-price-be-above-100000-on-may-31")
    token_id: str | None = os.getenv("POLYMARKET_TOKEN_ID")
    poll_interval_sec: int = int(os.getenv("POLL_INTERVAL_SEC", "15"))
    ma_window: int = int(os.getenv("MA_WINDOW", "12"))
    z_threshold: float = float(os.getenv("Z_THRESHOLD", "1.3"))
    order_size_usd: float = float(os.getenv("ORDER_SIZE_USD", "25"))
    max_position_usd: float = float(os.getenv("MAX_POSITION_USD", "200"))
    paper_mode: bool = os.getenv("PAPER_MODE", "true").lower() == "true"


settings = Settings()
