from rest_framework import generics, filters, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

from .models import Stock, Watchlist
from .serializers import StockSerializer, WatchlistSerializer


class StockListView(generics.ListAPIView):
    serializer_class = StockSerializer
    pagination_class = None  # return full list, no pagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["ticker", "name", "sector"]
    ordering_fields = ["ticker", "price", "change_percent", "market_cap"]

    def get_queryset(self):
        qs = Stock.objects.all()
        filter_type = self.request.query_params.get("filter")
        sector = self.request.query_params.get("sector")

        if filter_type == "gainers":
            qs = qs.filter(change__gt=0).order_by("-change_percent")
        elif filter_type == "losers":
            qs = qs.filter(change__lt=0).order_by("change_percent")
        elif filter_type == "active":
            qs = qs.order_by("-volume")

        if sector:
            qs = qs.filter(sector__iexact=sector)

        return qs


class StockDetailView(generics.RetrieveAPIView):
    serializer_class = StockSerializer
    queryset = Stock.objects.all()
    lookup_field = "ticker"


class WatchlistView(generics.ListCreateAPIView):
    serializer_class = WatchlistSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user).select_related("stock")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class WatchlistDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Watchlist.objects.filter(user=self.request.user)

