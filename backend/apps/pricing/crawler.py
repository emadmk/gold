"""TGJU crawler with a brsapi.ir fallback."""
from __future__ import annotations

import re
from decimal import Decimal

import httpx
from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from apps.audit.emit import emit_event


class TgjuCrawler:
    BASE = "https://www.tgju.org"
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (compatible; KeyhanGoldBot/1.0)",
        "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
    }
    PROFILES = {
        "gold_18k_750": "/profile/geram18",
        "gold_18k_740": "/profile/gold_740k",
        "gold_24k": "/profile/geram24",
        "mesghal": "/profile/mesghal",
        "gold_melted_cash": "/profile/gold_futures",
        "coin_emami": "/profile/sekee",
        "coin_bahar": "/profile/sekeb",
        "coin_half": "/profile/nim",
        "coin_quarter": "/profile/rob",
        "coin_gerami": "/profile/gerami",
        "silver_999": "/profile/silver_999",
        "silver_925": "/profile/silver_925",
        "ons_gold": "/profile/ons",
        "usd_free": "/profile/price_dollar_rl",
    }

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=4))
    async def fetch(self, key: str) -> Decimal:
        url = self.BASE + self.PROFILES[key]
        async with httpx.AsyncClient(timeout=10, headers=self.HEADERS) as c:
            r = await c.get(url, follow_redirects=True)
            r.raise_for_status()
        return self._parse(r.text)

    @staticmethod
    def _parse(html: str) -> Decimal:
        soup = BeautifulSoup(html, "lxml")
        # Method 1 — TGJU's primary attribute
        node = soup.select_one('[data-col="info.last_trade.PDrCotVal"]')
        if node and node.get_text(strip=True):
            return _to_decimal(node.get_text(strip=True))
        # Method 2 — meta tag
        meta = soup.find("meta", {"name": "price"})
        if meta and meta.get("content"):
            return _to_decimal(meta["content"])
        # Method 3 — regex
        m = re.search(r'data-price="([\d,]+)"', html)
        if m:
            return _to_decimal(m.group(1))
        raise ValueError("price node not found")


class BrsApiFallback:
    URL = "https://brsapi.ir/Api/Market/Gold_Currency.php"

    KEY_MAP = {
        "gold_18k_750": "IR_GOLD_18K",
        "gold_24k": "IR_GOLD_24K",
        "mesghal": "IR_MESQAL_17",
        "coin_emami": "IR_COIN_EMAMI",
        "coin_bahar": "IR_COIN_BAHAR",
        "coin_half": "IR_COIN_HALF",
        "coin_quarter": "IR_COIN_QUARTER",
        "coin_gerami": "IR_COIN_1G",
        "silver_999": "IR_SILVER_999",
        "usd_free": "USD",
        "ons_gold": "ONS",
    }

    async def fetch(self, key: str) -> Decimal:
        async with httpx.AsyncClient(timeout=10) as c:
            r = await c.get(self.URL)
            r.raise_for_status()
        data = r.json()
        src = self.KEY_MAP.get(key)
        if not src:
            raise KeyError(key)
        for row in data.get("gold", []) + data.get("currency", []):
            if row.get("symbol") == src or row.get("name") == src:
                return _to_decimal(str(row.get("price") or row.get("close")))
        raise ValueError(f"brsapi: {key!r} not found")


def _to_decimal(s: str) -> Decimal:
    s = (s or "").replace(",", "").replace("٬", "").strip()
    trans = str.maketrans("۰۱۲۳۴۵۶۷۸۹", "0123456789")
    return Decimal(s.translate(trans) or "0")


async def fetch_with_fallback(key: str) -> tuple[Decimal, str]:
    try:
        return await TgjuCrawler().fetch(key), "tgju"
    except Exception as exc:  # noqa: BLE001
        emit_event(
            "pricing.source.failover",
            severity="warning",
            outcome="failure",
            data={"source_key": key, "primary_error": repr(exc)},
        )
        return await BrsApiFallback().fetch(key), "brsapi"
