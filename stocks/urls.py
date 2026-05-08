from django.urls import path
from .views import StockListView, StockDetailView, WatchlistView, WatchlistDeleteView

urlpatterns = [
    path("", StockListView.as_view(), name="stock_list"),
    path("<str:ticker>/", StockDetailView.as_view(), name="stock_detail"),
    path("watchlist/", WatchlistView.as_view(), name="watchlist"),
    path("watchlist/<int:pk>/", WatchlistDeleteView.as_view(), name="watchlist_delete"),
]
