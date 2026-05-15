from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAdminUser
from django.contrib.auth import get_user_model
from django.db import transaction as db_transaction
from decimal import Decimal

from orders.models import Holding
from stocks.models import Stock
from wallet.models import Wallet, Transaction

from .serializers import (
    AdminUserListSerializer,
    AdminUserDetailSerializer,
    AdminHoldingSerializer,
)

User = get_user_model()


class AdminUserListView(generics.ListAPIView):
    """GET /api/admin/users/ — list all users with wallet & portfolio summary"""
    serializer_class = AdminUserListSerializer
    permission_classes = [IsAdminUser]
    pagination_class = None

    def get_queryset(self):
        qs = User.objects.prefetch_related("holdings__stock", "wallet").order_by("-date_joined")
        search = self.request.query_params.get("search", "")
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search)
            )
        return qs


class AdminUserDetailView(generics.RetrieveAPIView):
    """GET /api/admin/users/{id}/ — full user detail with holdings & transactions"""
    serializer_class = AdminUserDetailSerializer
    permission_classes = [IsAdminUser]

    def get_queryset(self):
        return User.objects.prefetch_related("holdings__stock", "transactions", "wallet").all()


class AdminAdjustWalletView(APIView):
    """POST /api/admin/users/{id}/wallet/ — set or adjust wallet balance"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        action = request.data.get("action")  # "set" | "add" | "subtract"
        try:
            amount = Decimal(str(request.data.get("amount", 0)))
        except Exception:
            return Response({"detail": "Invalid amount."}, status=status.HTTP_400_BAD_REQUEST)

        if amount < 0:
            return Response({"detail": "Amount must be non-negative."}, status=status.HTTP_400_BAD_REQUEST)

        wallet, _ = Wallet.objects.get_or_create(user=user)

        with db_transaction.atomic():
            if action == "set":
                old = wallet.balance
                wallet.balance = amount
                description = f"Admin set balance from ${old} to ${amount}"
            elif action == "add":
                wallet.balance += amount
                description = f"Admin credited ${amount}"
            elif action == "subtract":
                if wallet.balance < amount:
                    return Response({"detail": "Insufficient balance."}, status=status.HTTP_400_BAD_REQUEST)
                wallet.balance -= amount
                description = f"Admin debited ${amount}"
            else:
                return Response({"detail": "action must be set/add/subtract."}, status=status.HTTP_400_BAD_REQUEST)

            wallet.save()
            Transaction.objects.create(
                user=user,
                type="deposit" if action in ("set", "add") else "withdrawal",
                amount=amount,
                status="completed",
                description=description,
            )

        return Response({"balance": str(wallet.balance)})


class AdminHoldingView(APIView):
    """POST /api/admin/users/{id}/holdings/ — add or update a holding"""
    permission_classes = [IsAdminUser]

    def post(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        ticker = request.data.get("ticker", "").upper()
        try:
            shares = Decimal(str(request.data.get("shares", 0)))
            avg_cost = Decimal(str(request.data.get("avg_cost", 0)))
        except Exception:
            return Response({"detail": "Invalid shares or avg_cost."}, status=status.HTTP_400_BAD_REQUEST)

        if shares <= 0:
            return Response({"detail": "Shares must be positive."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            stock = Stock.objects.get(ticker=ticker)
        except Stock.DoesNotExist:
            return Response({"detail": f"Stock '{ticker}' not found."}, status=status.HTTP_404_NOT_FOUND)

        holding, created = Holding.objects.get_or_create(
            user=user, stock=stock,
            defaults={"shares": shares, "avg_cost": avg_cost},
        )
        if not created:
            holding.shares = shares
            holding.avg_cost = avg_cost
            holding.save()
        else:
            # Record a buy transaction so wallet history reflects the position
            Transaction.objects.create(
                user=user,
                type="buy",
                amount=shares * avg_cost,
                status="completed",
                description=f"Bought {shares} shares of {stock.ticker}",
            )

        return Response(AdminHoldingSerializer(holding).data, status=status.HTTP_200_OK)


class AdminHoldingDeleteView(APIView):
    """DELETE /api/admin/users/{user_id}/holdings/{holding_id}/"""
    permission_classes = [IsAdminUser]

    def delete(self, request, pk, holding_id):
        try:
            holding = Holding.objects.get(id=holding_id, user_id=pk)
        except Holding.DoesNotExist:
            return Response({"detail": "Holding not found."}, status=status.HTTP_404_NOT_FOUND)
        holding.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminUpdateUserView(APIView):
    """PATCH /api/admin/users/{id}/profile/ — update user account details"""
    permission_classes = [IsAdminUser]

    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
        except User.DoesNotExist:
            return Response({"detail": "User not found."}, status=status.HTTP_404_NOT_FOUND)

        allowed = ["first_name", "last_name", "email", "phone", "country", "is_active", "email_verified"]
        for field in allowed:
            if field in request.data:
                setattr(user, field, request.data[field])
        user.save()
        from .serializers import AdminUserDetailSerializer
        return Response(AdminUserDetailSerializer(user).data)

