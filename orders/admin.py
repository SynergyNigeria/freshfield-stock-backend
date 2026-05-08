from django.contrib import admin
from .models import Order, Holding

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "stock", "shares", "price_at_order", "total", "status", "created_at")
    list_filter = ("type", "status")
    search_fields = ("user__email", "stock__ticker")
    ordering = ("-created_at",)

@admin.register(Holding)
class HoldingAdmin(admin.ModelAdmin):
    list_display = ("user", "stock", "shares", "avg_cost", "updated_at")
    search_fields = ("user__email", "stock__ticker")
