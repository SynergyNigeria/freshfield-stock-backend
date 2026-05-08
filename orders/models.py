from django.db import models
from django.contrib.auth import get_user_model
from stocks.models import Stock

User = get_user_model()


class Holding(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="holdings")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    shares = models.DecimalField(max_digits=14, decimal_places=6)
    avg_cost = models.DecimalField(max_digits=12, decimal_places=4)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "stock")

    @property
    def current_value(self):
        return self.shares * self.stock.price

    @property
    def cost_basis(self):
        return self.shares * self.avg_cost

    @property
    def pnl(self):
        return self.current_value - self.cost_basis

    @property
    def pnl_percent(self):
        if self.cost_basis == 0:
            return 0
        return (self.pnl / self.cost_basis) * 100

    def __str__(self):
        return f"{self.user.email} — {self.shares} x {self.stock.ticker}"


class Order(models.Model):
    TYPE_CHOICES = [("buy", "Buy"), ("sell", "Sell")]
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("filled", "Filled"),
        ("failed", "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    type = models.CharField(max_length=4, choices=TYPE_CHOICES)
    shares = models.DecimalField(max_digits=14, decimal_places=6)
    price_at_order = models.DecimalField(max_digits=12, decimal_places=4)
    total = models.DecimalField(max_digits=14, decimal_places=2)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="filled")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} — {self.type} {self.shares} {self.stock.ticker} @ ${self.price_at_order}"

