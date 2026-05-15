from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.conf import settings
import resend

from .serializers import RegisterSerializer, UserSerializer, ChangePasswordSerializer
from .models import EmailVerificationToken

User = get_user_model()

resend.api_key = settings.RESEND_API_KEY


def send_verification_email(user, verify_url: str):
    html = f"""
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body style="margin:0;padding:0;background:#0d1a0d;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#0d1a0d;padding:40px 0;">
    <tr>
      <td align="center">
        <table width="520" cellpadding="0" cellspacing="0" style="background:#111f11;border-radius:16px;border:1px solid rgba(255,255,255,0.08);overflow:hidden;">
          <!-- Header -->
          <tr>
            <td style="background:#06d001;padding:28px 40px;text-align:center;">
              <span style="font-size:22px;font-weight:800;color:#000;letter-spacing:-0.5px;">Freshfield</span>
              <span style="font-size:14px;font-weight:500;color:rgba(0,0,0,0.6);margin-left:6px;">Stocks</span>
            </td>
          </tr>
          <!-- Body -->
          <tr>
            <td style="padding:40px;">
              <p style="margin:0 0 8px;font-size:22px;font-weight:700;color:#ffffff;">Verify your email</p>
              <p style="margin:0 0 28px;font-size:15px;color:rgba(255,255,255,0.5);line-height:1.6;">
                Hi {user.first_name}, welcome to Freshfield! Click the button below to activate your account.
              </p>
              <table cellpadding="0" cellspacing="0" width="100%">
                <tr>
                  <td align="center">
                    <a href="{verify_url}"
                       style="display:inline-block;background:#06d001;color:#000;font-weight:700;font-size:15px;
                              text-decoration:none;padding:14px 40px;border-radius:10px;letter-spacing:0.1px;">
                      Verify Email Address
                    </a>
                  </td>
                </tr>
              </table>
              <p style="margin:28px 0 0;font-size:13px;color:rgba(255,255,255,0.3);line-height:1.6;text-align:center;">
                Or copy this link into your browser:<br>
                <a href="{verify_url}" style="color:#06d001;word-break:break-all;">{verify_url}</a>
              </p>
            </td>
          </tr>
          <!-- Footer -->
          <tr>
            <td style="padding:20px 40px;border-top:1px solid rgba(255,255,255,0.06);text-align:center;">
              <p style="margin:0;font-size:12px;color:rgba(255,255,255,0.2);">
                If you didn&rsquo;t create a Freshfield account, you can safely ignore this email.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""
    resend.Emails.send({
        "from": settings.EMAIL_FROM,
        "to": [user.email],
        "subject": "Verify your Freshfield email address",
        "html": html,
    })


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        from wallet.models import Wallet
        Wallet.objects.get_or_create(user=user)

        token_obj = EmailVerificationToken.objects.create(user=user)
        verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token_obj.token}"
        try:
            send_verification_email(user, verify_url)
        except Exception as e:
            # Don't block registration if email fails; log the error
            import logging
            logging.getLogger(__name__).error("Resend email failed: %s", e)

        return Response(
            {"detail": "Account created. Please check your email to verify your address."},
            status=status.HTTP_201_CREATED,
        )


class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        token = request.data.get("token")
        if not token:
            return Response({"detail": "Token is required."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            token_obj = EmailVerificationToken.objects.select_related("user").get(token=token)
        except EmailVerificationToken.DoesNotExist:
            return Response({"detail": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user = token_obj.user
        user.email_verified = True
        user.is_active = True
        user.save(update_fields=["email_verified", "is_active"])
        token_obj.delete()

        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "user": UserSerializer(user).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            }
        )


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        if not user.check_password(serializer.validated_data["old_password"]):
            return Response({"old_password": "Incorrect password."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response({"detail": "Password updated."})


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"detail": "Logged out."})
        except Exception:
            return Response({"detail": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST)

