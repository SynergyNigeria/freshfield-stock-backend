from rest_framework import serializers
from .models import Wallet, Transaction, DepositRequest, WithdrawalRequest


class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ("id", "balance", "updated_at")


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ("id", "type", "amount", "status", "description", "created_at")


class DepositRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = DepositRequest
        fields = ("id", "amount", "proof_image", "status", "admin_note", "created_at")
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
