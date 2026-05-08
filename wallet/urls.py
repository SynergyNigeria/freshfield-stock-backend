from django.urls import path
from .views import (
    WalletView, TransactionListView,
    DepositRequestCreateView, DepositRequestListView,
    WithdrawalRequestCreateView, WithdrawalRequestListView,
)

urlpatterns = [
    path("", WalletView.as_view(), name="wallet"),
    path("transactions/", TransactionListView.as_view(), name="transactions"),
    path("deposit/", DepositRequestCreateView.as_view(), name="deposit_create"),
    path("deposits/", DepositRequestListView.as_view(), name="deposit_list"),
    path("withdraw/", WithdrawalRequestCreateView.as_view(), name="withdrawal_create"),
    path("withdrawals/", WithdrawalRequestListView.as_view(), name="withdrawal_list"),
]
