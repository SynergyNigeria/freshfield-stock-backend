from django.contrib import admin
from .models import Wallet, Transaction, DepositRequest, WithdrawalRequest

@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ("user", "balance")
    search_fields = ("user__email",)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ("user", "type", "amount", "status", "created_at")
    list_filter = ("type", "status")
    search_fields = ("user__email",)

@admin.register(DepositRequest)
class DepositRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__email",)
    actions = ["approve_deposits"]

    def approve_deposits(self, request, queryset):
        from wallet.models import Transaction
        for deposit in queryset.filter(status="pending"):
            deposit.status = "approved"
            deposit.save()
            deposit.user.wallet.balance += deposit.amount
            deposit.user.wallet.save()
            Transaction.objects.filter(
                user=deposit.user, type="deposit",
                description__icontains=str(deposit.amount), status="pending"
            ).update(status="completed")
        self.message_user(request, "Selected deposits approved.")
    approve_deposits.short_description = "Approve selected deposits"

@admin.register(WithdrawalRequest)
class WithdrawalRequestAdmin(admin.ModelAdmin):
    list_display = ("user", "amount", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__email",)
