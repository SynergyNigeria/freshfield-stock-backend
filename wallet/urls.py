from django.urls import path
from .views import (
    WalletView, TransactionListView,
    DepositRequestCreateView, DepositRequestListView,
    WithdrawalRequestCreateView, WithdrawalRequestListView,
    TransferMethodListView,
    AdminTransferMethodListCreateView, AdminTransferMethodDetailView,
)

urlpatterns = [
    path("", WalletView.as_view(), name="wallet"),
    path("transactions/", TransactionListView.as_view(), name="transactions"),
    path("deposit/", DepositRequestCreateView.as_view(), name="deposit_create"),
    path("deposits/", DepositRequestListView.as_view(), name="deposit_list"),
    path("withdraw/", WithdrawalRequestCreateView.as_view(), name="withdrawal_create"),
    path("withdrawals/", WithdrawalRequestListView.as_view(), name="withdrawal_list"),
    path("transfer-methods/", TransferMethodListView.as_view(), name="transfer_methods"),
    path("admin/transfer-methods/", AdminTransferMethodListCreateView.as_view(), name="admin_transfer_methods"),
    path("admin/transfer-methods/<int:pk>/", AdminTransferMethodDetailView.as_view(), name="admin_transfer_method_detail"),
]
