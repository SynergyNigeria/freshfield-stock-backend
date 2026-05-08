from rest_framework import serializers
from stocks.serializers import StockSerializer
from .models import Order, Holding


class OrderSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    ticker = serializers.CharField(write_only=True)
    shares = serializers.DecimalField(max_digits=14, decimal_places=6)

    class Meta:
        model = Order
        fields = ("id", "stock", "ticker", "type", "shares", "price_at_order", "total", "status", "created_at")
        read_only_fields = ("price_at_order", "total", "status", "created_at", "stock")

    def validate_shares(self, value):
        if value <= 0:
            raise serializers.ValidationError("Shares must be greater than zero.")
        return value

    def validate(self, data):
        from stocks.models import Stock
        ticker = data.pop("ticker")
        try:
            stock = Stock.objects.get(ticker=ticker.upper())
        except Stock.DoesNotExist:
            raise serializers.ValidationError({"ticker": f"Stock '{ticker}' not found."})

        data["stock"] = stock
        data["price_at_order"] = stock.price
        data["total"] = round(data["shares"] * stock.price, 2)

        user = self.context["request"].user
        wallet = user.wallet

        if data["type"] == "buy":
            if data["total"] > wallet.balance:
                raise serializers.ValidationError({"shares": "Insufficient wallet balance."})
        elif data["type"] == "sell":
            holding = Holding.objects.filter(user=user, stock=stock).first()
            if not holding or holding.shares < data["shares"]:
                raise serializers.ValidationError({"shares": "You don't have enough shares to sell."})

        return data


class HoldingSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    current_value = serializers.ReadOnlyField()
    cost_basis = serializers.ReadOnlyField()
    pnl = serializers.ReadOnlyField()
    pnl_percent = serializers.ReadOnlyField()

    class Meta:
        model = Holding
        fields = ("id", "stock", "shares", "avg_cost", "current_value", "cost_basis", "pnl", "pnl_percent", "updated_at")
