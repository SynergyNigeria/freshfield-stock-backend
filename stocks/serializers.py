from rest_framework import serializers
from .models import Stock, Watchlist


class StockSerializer(serializers.ModelSerializer):
    logo = serializers.ReadOnlyField()
    is_positive = serializers.SerializerMethodField()

    class Meta:
        model = Stock
        fields = (
            "id", "ticker", "name", "sector", "price", "change",
            "change_percent", "volume", "market_cap", "high_52w",
            "low_52w", "pe", "dividend", "logo", "is_positive", "updated_at",
        )

    def get_is_positive(self, obj):
        return obj.change >= 0


class WatchlistSerializer(serializers.ModelSerializer):
    stock = StockSerializer(read_only=True)
    stock_id = serializers.PrimaryKeyRelatedField(
        queryset=Stock.objects.all(), source="stock", write_only=True
    )

    class Meta:
        model = Watchlist
        fields = ("id", "stock", "stock_id", "added_at")
