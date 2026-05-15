from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db import transaction as db_transaction

from wallet.models import Transaction as WalletTransaction
from .models import Order, Holding
from .serializers import OrderSerializer, HoldingSerializer


class PlaceOrderView(generics.CreateAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        with db_transaction.atomic():
            order = serializer.save(user=self.request.user)
            wallet = self.request.user.wallet

            if order.type == "buy":
                # Deduct from wallet
                wallet.balance -= order.total
                wallet.save()

                # Update or create holding
                holding, created = Holding.objects.get_or_create(
                    user=self.request.user,
                    stock=order.stock,
                    defaults={"shares": 0, "avg_cost": 0},
                )
                # Weighted average cost
                total_shares = holding.shares + order.shares
                holding.avg_cost = (
                    (holding.shares * holding.avg_cost + order.shares * order.price_at_order)
                    / total_shares
                )
                holding.shares = total_shares
                holding.save()

                WalletTransaction.objects.create(
                    user=self.request.user,
                    type="buy",
                    amount=order.total,
                    status="completed",
                    description=f"Bought {order.shares} shares of {order.stock.ticker}",
                )

            elif order.type == "sell":
                # Credit wallet
                wallet.balance += order.total
                wallet.save()

                # Reduce holding
                holding = Holding.objects.get(user=self.request.user, stock=order.stock)
                holding.shares -= order.shares
                if holding.shares <= 0:
                    holding.delete()
                else:
                    holding.save()

                WalletTransaction.objects.create(
                    user=self.request.user,
                    type="sell",
                    amount=order.total,
                    status="completed",
                    description=f"Sold {order.shares} shares of {order.stock.ticker}",
                )


class OrderHistoryView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).select_related("stock")


class PortfolioView(generics.ListAPIView):
    serializer_class = HoldingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Holding.objects.filter(user=self.request.user).select_related("stock")

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        holdings = HoldingSerializer(qs, many=True).data

        total_value = sum(float(h["current_value"]) for h in holdings)
        total_cost = sum(float(h["cost_basis"]) for h in holdings)
        total_pnl = total_value - total_cost
        total_pnl_pct = (total_pnl / total_cost * 100) if total_cost > 0 else 0

        return Response({
            "holdings": holdings,
            "summary": {
                "total_value": round(total_value, 2),
                "total_cost": round(total_cost, 2),
                "total_pnl": round(total_pnl, 2),
                "total_pnl_percent": round(total_pnl_pct, 4),
            },
        })

