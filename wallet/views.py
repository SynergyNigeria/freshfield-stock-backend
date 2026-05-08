from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from django.db import transaction as db_transaction

from .models import Wallet, Transaction, DepositRequest, WithdrawalRequest
from .serializers import (
    WalletSerializer, TransactionSerializer,
    DepositRequestSerializer, WithdrawalRequestSerializer,
)


class WalletView(generics.RetrieveAPIView):
    serializer_class = WalletSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        wallet, _ = Wallet.objects.get_or_create(user=self.request.user)
        return wallet


class TransactionListView(generics.ListAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user)


class DepositRequestCreateView(generics.CreateAPIView):
    serializer_class = DepositRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        deposit = serializer.save(user=self.request.user)
        # Log a pending transaction
        Transaction.objects.create(
            user=self.request.user,
            type="deposit",
            amount=deposit.amount,
            status="pending",
            description="Bank transfer deposit — pending verification",
        )


class DepositRequestListView(generics.ListAPIView):
    serializer_class = DepositRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return DepositRequest.objects.filter(user=self.request.user)


class WithdrawalRequestCreateView(generics.CreateAPIView):
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        with db_transaction.atomic():
            withdrawal = serializer.save(user=self.request.user)
            # Hold funds immediately
            wallet = self.request.user.wallet
            wallet.balance -= withdrawal.amount
            wallet.save()
            Transaction.objects.create(
                user=self.request.user,
                type="withdrawal",
                amount=withdrawal.amount,
                status="pending",
                description=f"Withdrawal to {withdrawal.bank_name}",
            )


class WithdrawalRequestListView(generics.ListAPIView):
    serializer_class = WithdrawalRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WithdrawalRequest.objects.filter(user=self.request.user)

