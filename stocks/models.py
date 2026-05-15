from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Stock(models.Model):
    ticker = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=4)
    change = models.DecimalField(max_digits=10, decimal_places=4, default=0)
    change_percent = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    volume = models.CharField(max_length=20, blank=True)
    market_cap = models.CharField(max_length=20, blank=True)
    high_52w = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    low_52w = models.DecimalField(max_digits=12, decimal_places=4, default=0)
    pe = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    dividend = models.DecimalField(max_digits=8, decimal_places=4, default=0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.ticker

    class Meta:
        ordering = ["ticker"]

    @property
    def logo(self):
        return f"https://financialmodelingprep.com/image-stock/{self.ticker}.png"


class Watchlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchlist")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "stock")

    def __str__(self):
        return f"{self.user.email} — {self.stock.ticker}"

