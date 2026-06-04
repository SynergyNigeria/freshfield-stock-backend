"""
Fetch live stock prices from Financial Modeling Prep (FMP) API and update the database.

Free tier: 250 requests/day  →  batch all tickers in one request.

Setup:
  1. Sign up free at https://financialmodelingprep.com/developer/docs
  2. Add to your PythonAnywhere .env:
       FMP_API_KEY=your_key_here
  3. Schedule as a daily task in PythonAnywhere "Tasks" tab:
       source /home/freshfieldstock/.virtualenvs/freshfield/bin/activate &&
       cd /home/freshfieldstock/freshfield-stock-backend &&
       python manage.py update_prices

Note: SpaceX (SPACEX) is private — FMP won't have it.
      Its price will be skipped and remain at the manually set value.
"""

import urllib.request
import json
import logging
from decimal import Decimal, InvalidOperation

from django.core.management.base import BaseCommand
from django.conf import settings

from stocks.models import Stock

logger = logging.getLogger(__name__)


def _fmt(val, default="0"):
    try:
        return str(Decimal(str(val)).quantize(Decimal("0.0001")))
    except (InvalidOperation, TypeError):
        return default


class Command(BaseCommand):
    help = "Fetch live prices from FMP API and update all stocks"

    def handle(self, *args, **options):
        api_key = getattr(settings, "FMP_API_KEY", None)
        if not api_key:
            self.stderr.write("FMP_API_KEY not set in settings / .env — aborting.")
            return

        tickers = list(Stock.objects.values_list("ticker", flat=True))
        # FMP doesn't carry private tickers like SPACEX — skip them
        public_tickers = [t for t in tickers if t != "SPACEX"]

        if not public_tickers:
            self.stdout.write("No public tickers to update.")
            return

        updated = 0
        for ticker in public_tickers:
            url = f"https://financialmodelingprep.com/stable/quote?symbol={ticker}&apikey={api_key}"
            try:
                req = urllib.request.Request(
                    url,
                    headers={"User-Agent": "Mozilla/5.0 (compatible; FreshfieldStocks/1.0)"},
                )
                with urllib.request.urlopen(req, timeout=15) as resp:
                    data = json.loads(resp.read().decode())
            except Exception as exc:
                self.stderr.write(f"FMP request failed for {ticker}: {exc}")
                continue

            if not isinstance(data, list) or not data:
                self.stderr.write(f"No data for {ticker}: {data}")
                continue

            item = data[0]
            try:
                stock = Stock.objects.get(ticker=ticker)
            except Stock.DoesNotExist:
                continue

            stock.price = _fmt(item.get("price", stock.price))
            stock.change = _fmt(item.get("change", stock.change))
            stock.change_percent = _fmt(item.get("changePercentage", stock.change_percent))
            stock.volume = str(item.get("volume") or stock.volume)
            stock.market_cap = str(item.get("marketCap") or stock.market_cap)
            stock.high_52w = _fmt(item.get("yearHigh", stock.high_52w))
            stock.low_52w = _fmt(item.get("yearLow", stock.low_52w))
            stock.pe = _fmt(item.get("pe", stock.pe), default="0.00")
            stock.save()
            updated += 1

        self.stdout.write(self.style.SUCCESS(f"Updated {updated} stocks."))
