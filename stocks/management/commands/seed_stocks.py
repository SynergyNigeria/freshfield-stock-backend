from django.core.management.base import BaseCommand
from stocks.models import Stock
from decimal import Decimal


SEED_STOCKS = [
    {
        "ticker": "AAPL", "name": "Apple Inc.", "sector": "Technology",
        "price": "213.49", "change": "2.15", "change_percent": "1.02",
        "volume": 54_200_000, "market_cap": 3_290_000_000_000,
        "high_52w": "237.23", "low_52w": "164.08",
        "pe": "33.2", "dividend": "0.96",
    },
    {
        "ticker": "MSFT", "name": "Microsoft Corp.", "sector": "Technology",
        "price": "415.32", "change": "3.80", "change_percent": "0.92",
        "volume": 21_500_000, "market_cap": 3_090_000_000_000,
        "high_52w": "468.35", "low_52w": "309.45",
        "pe": "36.8", "dividend": "3.00",
    },
    {
        "ticker": "GOOGL", "name": "Alphabet Inc.", "sector": "Technology",
        "price": "178.02", "change": "-1.23", "change_percent": "-0.69",
        "volume": 18_700_000, "market_cap": 2_210_000_000_000,
        "high_52w": "207.05", "low_52w": "130.67",
        "pe": "23.4", "dividend": "0.00",
    },
    {
        "ticker": "AMZN", "name": "Amazon.com Inc.", "sector": "Consumer Cyclical",
        "price": "197.12", "change": "1.45", "change_percent": "0.74",
        "volume": 32_100_000, "market_cap": 2_090_000_000_000,
        "high_52w": "242.52", "low_52w": "151.61",
        "pe": "41.5", "dividend": "0.00",
    },
    {
        "ticker": "NVDA", "name": "NVIDIA Corp.", "sector": "Technology",
        "price": "131.38", "change": "4.22", "change_percent": "3.32",
        "volume": 290_000_000, "market_cap": 3_220_000_000_000,
        "high_52w": "153.13", "low_52w": "47.32",
        "pe": "52.6", "dividend": "0.04",
    },
    {
        "ticker": "META", "name": "Meta Platforms Inc.", "sector": "Communication Services",
        "price": "558.12", "change": "-4.30", "change_percent": "-0.76",
        "volume": 14_500_000, "market_cap": 1_420_000_000_000,
        "high_52w": "740.91", "low_52w": "392.39",
        "pe": "28.7", "dividend": "0.00",
    },
    {
        "ticker": "TSLA", "name": "Tesla Inc.", "sector": "Consumer Cyclical",
        "price": "247.15", "change": "6.72", "change_percent": "2.80",
        "volume": 95_600_000, "market_cap": 791_000_000_000,
        "high_52w": "488.54", "low_52w": "138.80",
        "pe": "68.3", "dividend": "0.00",
    },
    {
        "ticker": "BRK.B", "name": "Berkshire Hathaway Inc.", "sector": "Financial Services",
        "price": "444.92", "change": "0.88", "change_percent": "0.20",
        "volume": 3_100_000, "market_cap": 971_000_000_000,
        "high_52w": "496.49", "low_52w": "373.52",
        "pe": "21.0", "dividend": "0.00",
    },
    {
        "ticker": "V", "name": "Visa Inc.", "sector": "Financial Services",
        "price": "279.52", "change": "1.05", "change_percent": "0.38",
        "volume": 6_800_000, "market_cap": 567_000_000_000,
        "high_52w": "354.44", "low_52w": "259.47",
        "pe": "30.5", "dividend": "2.36",
    },
    {
        "ticker": "JNJ", "name": "Johnson & Johnson", "sector": "Healthcare",
        "price": "157.88", "change": "-0.45", "change_percent": "-0.28",
        "volume": 7_200_000, "market_cap": 380_000_000_000,
        "high_52w": "175.87", "low_52w": "143.13",
        "pe": "15.6", "dividend": "4.76",
    },
    {
        "ticker": "WMT", "name": "Walmart Inc.", "sector": "Consumer Defensive",
        "price": "96.42", "change": "0.65", "change_percent": "0.68",
        "volume": 12_300_000, "market_cap": 773_000_000_000,
        "high_52w": "105.30", "low_52w": "60.15",
        "pe": "37.8", "dividend": "0.83",
    },
    {
        "ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector": "Financial Services",
        "price": "214.62", "change": "2.10", "change_percent": "0.99",
        "volume": 9_400_000, "market_cap": 611_000_000_000,
        "high_52w": "280.25", "low_52w": "183.95",
        "pe": "12.8", "dividend": "5.00",
    },
    {
        "ticker": "PG", "name": "Procter & Gamble Co.", "sector": "Consumer Defensive",
        "price": "165.20", "change": "-0.30", "change_percent": "-0.18",
        "volume": 5_900_000, "market_cap": 390_000_000_000,
        "high_52w": "179.60", "low_52w": "152.37",
        "pe": "27.4", "dividend": "3.76",
    },
    {
        "ticker": "UNH", "name": "UnitedHealth Group Inc.", "sector": "Healthcare",
        "price": "483.74", "change": "-3.50", "change_percent": "-0.72",
        "volume": 4_200_000, "market_cap": 447_000_000_000,
        "high_52w": "630.73", "low_52w": "440.35",
        "pe": "18.9", "dividend": "8.00",
    },
    {
        "ticker": "HD", "name": "The Home Depot Inc.", "sector": "Consumer Cyclical",
        "price": "345.10", "change": "1.80", "change_percent": "0.52",
        "volume": 3_700_000, "market_cap": 342_000_000_000,
        "high_52w": "395.00", "low_52w": "309.95",
        "pe": "25.6", "dividend": "9.00",
    },
    {
        "ticker": "MA", "name": "Mastercard Inc.", "sector": "Financial Services",
        "price": "467.50", "change": "2.35", "change_percent": "0.51",
        "volume": 2_600_000, "market_cap": 428_000_000_000,
        "high_52w": "537.15", "low_52w": "420.26",
        "pe": "36.0", "dividend": "2.64",
    },
    {
        "ticker": "ABBV", "name": "AbbVie Inc.", "sector": "Healthcare",
        "price": "189.62", "change": "-1.10", "change_percent": "-0.58",
        "volume": 4_800_000, "market_cap": 335_000_000_000,
        "high_52w": "211.37", "low_52w": "155.03",
        "pe": "56.2", "dividend": "6.20",
    },
    {
        "ticker": "COST", "name": "Costco Wholesale Corp.", "sector": "Consumer Defensive",
        "price": "888.57", "change": "5.20", "change_percent": "0.59",
        "volume": 1_900_000, "market_cap": 393_000_000_000,
        "high_52w": "1078.23", "low_52w": "723.24",
        "pe": "55.8", "dividend": "4.64",
    },
    {
        "ticker": "NFLX", "name": "Netflix Inc.", "sector": "Communication Services",
        "price": "718.42", "change": "8.90", "change_percent": "1.25",
        "volume": 6_100_000, "market_cap": 307_000_000_000,
        "high_52w": "1064.50", "low_52w": "538.04",
        "pe": "44.3", "dividend": "0.00",
    },
    {
        "ticker": "DIS", "name": "The Walt Disney Co.", "sector": "Communication Services",
        "price": "104.20", "change": "-0.90", "change_percent": "-0.86",
        "volume": 8_500_000, "market_cap": 189_000_000_000,
        "high_52w": "123.74", "low_52w": "83.91",
        "pe": "35.7", "dividend": "0.00",
    },
]


class Command(BaseCommand):
    help = "Seed the database with 20 US stock records"

    def handle(self, *args, **options):
        created_count = 0
        updated_count = 0

        for data in SEED_STOCKS:
            stock, created = Stock.objects.update_or_create(
                ticker=data["ticker"],
                defaults={
                    "name": data["name"],
                    "sector": data["sector"],
                    "price": Decimal(data["price"]),
                    "change": Decimal(data["change"]),
                    "change_percent": Decimal(data["change_percent"]),
                    "volume": data["volume"],
                    "market_cap": data["market_cap"],
                    "high_52w": Decimal(data["high_52w"]),
                    "low_52w": Decimal(data["low_52w"]),
                    "pe": Decimal(data["pe"]),
                    "dividend": Decimal(data["dividend"]),
                },
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Seed complete: {created_count} created, {updated_count} updated."
            )
        )
