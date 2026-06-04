from rest_framework import serializers
from .models import Wallet, Transaction, DepositRequest, WithdrawalRequest, TransferMethod


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ("id", "balance", "updated_at")


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("id", "type", "amount", "status", "description", "created_at")


class TransferMethodSerializer(serializers.ModelSerializer):
    method_type_display = serializers.CharField(source="get_method_type_display", read_only=True)

    class Meta:
        model = TransferMethod
        fields = (
            "id", "method_type", "method_type_display", "display_name",
            "account_name", "account_identifier", "bank_name",
            "routing_number", "reference", "instructions", "is_active", "order",
        )


class DepositRequestSerializer(serializers.ModelSerializer):
    transfer_method_id = serializers.PrimaryKeyRelatedField(
        queryset=TransferMethod.objects.filter(is_active=True),
        source="transfer_method",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = DepositRequest
        fields = ("id", "amount", "proof_image", "transfer_method_id", "status", "admin_note", "created_at")
        read_only_fields = ("status", "admin_note", "created_at")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value


class WithdrawalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = WithdrawalRequest
        fields = (
            "id", "amount", "bank_name", "account_number", "account_name",
            "routing_number", "status", "admin_note", "created_at",
        )
        read_only_fields = ("status", "admin_note", "created_at")

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate(self, data):
        user = self.context["request"].user
        wallet = user.wallet
        if data["amount"] > wallet.balance:
            raise serializers.ValidationError({"amount": "Insufficient balance."})
        return data
