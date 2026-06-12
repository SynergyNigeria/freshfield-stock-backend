from rest_framework import serializers
from rest_framework_simplejwt.settings import api_settings
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    email = serializers.CharField(required=False, write_only=True)
    login = serializers.CharField(required=False, write_only=True)
    user_id = serializers.IntegerField(required=False, write_only=True)
    password = serializers.CharField(write_only=True, trim_whitespace=False)
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    default_error_messages = {
        "no_active_account": "No active account found with the given credentials."
    }

    def validate(self, attrs):
        identifier = attrs.get("login") or attrs.get("email") or attrs.get("user_id")
        password = attrs.get("password")

        if not identifier or not password:
            raise serializers.ValidationError("Email or ID and password are required.")

        user = None
        identifier = str(identifier).strip()

        if identifier.isdigit():
            user = User.objects.filter(pk=int(identifier)).first()
        else:
            user = User.objects.filter(email__iexact=identifier).first()

        if user:
            user = authenticate(
                request=self.context.get("request"),
                email=user.email,
                password=password,
            )

        if not api_settings.USER_AUTHENTICATION_RULE(user):
            raise serializers.ValidationError(
                {"detail": self.error_messages["no_active_account"]},
                code="no_active_account",
            )

        refresh = RefreshToken.for_user(user)
        return {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
        }


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone", "country", "password", "password2")

    def validate(self, data):
        if data["password"] != data["password2"]:
            raise serializers.ValidationError({"password": "Passwords do not match."})
        return data

    def create(self, validated_data):
        validated_data.pop("password2")
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ("id", "email", "first_name", "last_name", "full_name", "phone", "country", "email_verified", "date_joined")
        read_only_fields = ("id", "date_joined", "email_verified")


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True, validators=[validate_password])
