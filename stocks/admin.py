from django.contrib import admin
from .models import Stock, Watchlist

@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("ticker", "name", "sector", "price", "change_percent", "updated_at")
    search_fields = ("ticker", "name", "sector")
    ordering = ("ticker",)

@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display = ("user", "stock")
    search_fields = ("user__email", "stock__ticker")
