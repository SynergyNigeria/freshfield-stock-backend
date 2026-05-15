from rest_framework import serializers
from django.contrib.auth import get_user_model
from orders.models import Holding
from stocks.models import Stock
from wallet.models import Wallet, Transaction

User = get_user_model()


class AdminStockBriefSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stock
        fields = ("id", "ticker", "name", "price")


class AdminHoldingSerializer(serializers.ModelSerializer):
    stock = AdminStockBriefSerializer(read_only=True)
    stock_id = serializers.PrimaryKeyRelatedField(
        queryset=Stock.objects.all(), source="stock", write_only=True
    )
    current_value = serializers.ReadOnlyField()
    cost_basis = serializers.ReadOnlyField()
    pnl = serializers.ReadOnlyField()
    pnl_percent = serializers.ReadOnlyField()

    class Meta:
        model = Holding
        fields = (
            "id", "stock", "stock_id", "shares", "avg_cost",
            "current_value", "cost_basis", "pnl", "pnl_percent",
        )


class AdminWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ("balance",)


class AdminTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("id", "type", "amount", "status", "description", "created_at")


class AdminUserListSerializer(serializers.ModelSerializer):
    wallet_balance = serializers.SerializerMethodField()
    portfolio_value = serializers.SerializerMethodField()
    holdings_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            "id", "email", "first_name", "last_name", "country", "phone",
            "email_verified", "is_active", "date_joined",
            "wallet_balance", "portfolio_value", "holdings_count",
        )

    def get_wallet_balance(self, obj):
        try:
            return str(obj.wallet.balance)
        except Exception:
            return "0.00"

    def get_portfolio_value(self, obj):
        total = sum(h.current_value for h in obj.holdings.select_related("stock").all())
        return str(total)

    def get_holdings_count(self, obj):
        return obj.holdings.count()


class AdminUserDetailSerializer(AdminUserListSerializer):
    holdings = AdminHoldingSerializer(many=True, read_only=True)
    recent_transactions = serializers.SerializerMethodField()

    class Meta(AdminUserListSerializer.Meta):
        fields = AdminUserListSerializer.Meta.fields + ("holdings", "recent_transactions")

    def get_recent_transactions(self, obj):
        qs = obj.transactions.order_by("-created_at")[:20]
        return AdminTransactionSerializer(qs, many=True).data
