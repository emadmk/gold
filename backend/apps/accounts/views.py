"""Auth + profile + KYC API views."""
from __future__ import annotations

from django.conf import settings
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from apps.audit.emit import emit_event

from .models import KYCSubmission
from .permissions import IsAdminRole
from .serializers import (
    KYCSubmissionSerializer,
    OTPVerifySerializer,
    PhoneSerializer,
    UserSerializer,
)
from .services import kyc as kyc_svc
from .services import otp as otp_svc
from .services import totp as totp_svc


def _set_jwt_cookies(response: Response, refresh: RefreshToken) -> Response:
    cfg = settings.SIMPLE_JWT
    access = str(refresh.access_token)
    response.set_cookie(
        cfg["AUTH_COOKIE"], access,
        httponly=cfg["AUTH_COOKIE_HTTP_ONLY"], secure=cfg["AUTH_COOKIE_SECURE"],
        samesite=cfg["AUTH_COOKIE_SAMESITE"],
        max_age=int(cfg["ACCESS_TOKEN_LIFETIME"].total_seconds()),
    )
    response.set_cookie(
        cfg["AUTH_COOKIE_REFRESH"], str(refresh),
        httponly=True, secure=cfg["AUTH_COOKIE_SECURE"],
        samesite=cfg["AUTH_COOKIE_SAMESITE"],
        max_age=int(cfg["REFRESH_TOKEN_LIFETIME"].total_seconds()),
    )
    return response


class OTPRequestView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = PhoneSerializer(data=request.data)
        s.is_valid(raise_exception=True)
        otp_svc.request_otp(s.validated_data["phone"], purpose="login")
        # The code itself is never returned in the response — it is sent by
        # SMS. The Kavenegar response acknowledges delivery via the
        # `accounts.otp.delivered` event in Kibana.
        return Response(
            {"detail": "کد به شماره موبایل ارسال شد."},
            status=status.HTTP_202_ACCEPTED,
        )


class OTPVerifyView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        s = OTPVerifySerializer(data=request.data)
        s.is_valid(raise_exception=True)
        phone = s.validated_data["phone"]
        code = s.validated_data["code"]
        if not otp_svc.verify_otp(phone, code, purpose="login"):
            return Response({"detail": "کد وارد شده صحیح یا معتبر نیست."},
                            status=status.HTTP_400_BAD_REQUEST)
        user, created = otp_svc.upsert_user(phone)
        # Make sure wallets exist on first login
        from apps.wallet.services import ensure_wallets
        ensure_wallets(user)
        refresh = RefreshToken.for_user(user)
        resp = Response(
            {"user": UserSerializer(user).data, "is_new": created},
            status=status.HTTP_200_OK,
        )
        _set_jwt_cookies(resp, refresh)
        emit_event(
            "accounts.session.opened",
            actor={"type": "user", "id": str(user.id)},
            target={"type": "user", "id": str(user.id)},
        )
        return resp


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh = request.COOKIES.get(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])
            if refresh:
                RefreshToken(refresh).blacklist()
        except Exception:  # noqa: BLE001
            pass
        resp = Response({"detail": "خروج با موفقیت انجام شد."})
        resp.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE"])
        resp.delete_cookie(settings.SIMPLE_JWT["AUTH_COOKIE_REFRESH"])
        emit_event(
            "accounts.session.revoked",
            actor={"type": "user", "id": str(request.user.id)},
            target={"type": "user", "id": str(request.user.id)},
        )
        return resp


class MeView(APIView):
    def get(self, request):
        return Response(UserSerializer(request.user).data)

    def patch(self, request):
        u = request.user
        for f in ("first_name", "last_name", "email", "address", "postal_code",
                  "father_name", "share_trades"):
            if f in request.data:
                setattr(u, f, request.data[f])
        u.save()
        return Response(UserSerializer(u).data)


class KYCView(APIView):
    """Submit / re-submit KYC documents."""

    def get(self, request):
        sub = KYCSubmission.objects.filter(user=request.user).first()
        if not sub:
            return Response({"state": "empty"})
        return Response(KYCSubmissionSerializer(sub).data)

    def post(self, request):
        files = {
            k: request.FILES.get(k)
            for k in (
                "national_card_front",
                "national_card_back",
                "selfie_with_card",
                "birth_certificate",
                "video_attestation",
            )
        }
        sub = kyc_svc.submit_kyc(request.user, **files)
        return Response(KYCSubmissionSerializer(sub).data, status=status.HTTP_201_CREATED)


class KYCAdminApproveView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, submission_id: str):
        sub = KYCSubmission.objects.get(id=submission_id)
        if sub.state == "submitted":
            kyc_svc.start_review(sub, reviewer=request.user)
        kyc_svc.approve(sub, reviewer=request.user)
        return Response(KYCSubmissionSerializer(sub).data)


class KYCAdminRejectView(APIView):
    permission_classes = [IsAuthenticated, IsAdminRole]

    def post(self, request, submission_id: str):
        sub = KYCSubmission.objects.get(id=submission_id)
        if sub.state == "submitted":
            kyc_svc.start_review(sub, reviewer=request.user)
        reason = request.data.get("reason", "")
        kyc_svc.reject(sub, reviewer=request.user, reason=reason)
        return Response(KYCSubmissionSerializer(sub).data)


# ---------------------------------------------------------------------------
# 2FA (TOTP)
# ---------------------------------------------------------------------------

class TwoFactorEnrollView(APIView):
    """Generate a TOTP secret and provisioning URI for the user."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.two_factor_enabled:
            return Response({"detail": "۲FA پیش‌تر فعال شده است."}, status=400)
        secret = totp_svc.generate_secret()
        request.user.two_factor_secret = secret
        request.user.save(update_fields=["two_factor_secret"])
        uri = totp_svc.provisioning_uri(secret, request.user.phone)
        return Response({"secret": secret, "otpauth": uri})


class TwoFactorConfirmView(APIView):
    """Confirm the enrollment by verifying a fresh code."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code", "")
        if not totp_svc.verify(request.user.two_factor_secret, code):
            return Response({"detail": "کد TOTP نامعتبر است."}, status=400)
        request.user.two_factor_enabled = True
        request.user.save(update_fields=["two_factor_enabled"])
        return Response({"detail": "تأیید دوعاملی فعال شد."})


class TwoFactorDisableView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = request.data.get("code", "")
        if not totp_svc.verify(request.user.two_factor_secret, code):
            return Response({"detail": "کد TOTP نامعتبر است."}, status=400)
        request.user.two_factor_enabled = False
        request.user.two_factor_secret = ""
        request.user.save(update_fields=["two_factor_enabled", "two_factor_secret"])
        return Response({"detail": "تأیید دوعاملی غیرفعال شد."})
