from django.urls import path
from .views import (
    AdminUserListView,
    AdminUserDetailView,
    AdminAdjustWalletView,
    AdminHoldingView,
    AdminHoldingDeleteView,
    AdminUpdateUserView,
)

urlpatterns = [
    path("users/", AdminUserListView.as_view(), name="admin_users"),
    path("users/<int:pk>/", AdminUserDetailView.as_view(), name="admin_user_detail"),
    path("users/<int:pk>/profile/", AdminUpdateUserView.as_view(), name="admin_user_profile"),
    path("users/<int:pk>/wallet/", AdminAdjustWalletView.as_view(), name="admin_wallet"),
    path("users/<int:pk>/holdings/", AdminHoldingView.as_view(), name="admin_holdings"),
    path("users/<int:pk>/holdings/<int:holding_id>/", AdminHoldingDeleteView.as_view(), name="admin_holding_delete"),
]
