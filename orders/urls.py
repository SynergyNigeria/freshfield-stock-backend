from django.urls import path
from .views import PlaceOrderView, OrderHistoryView, PortfolioView

urlpatterns = [
    path("", PlaceOrderView.as_view(), name="place_order"),
    path("history/", OrderHistoryView.as_view(), name="order_history"),
    path("portfolio/", PortfolioView.as_view(), name="portfolio"),
]
