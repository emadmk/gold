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
        debug_code = otp_svc.request_otp(s.validated_data["phone"], purpose="login")
        body: dict[str, str] = {"detail": "کد به شماره موبایل ارسال شد."}
        if debug_code:
            body["debug_code"] = debug_code  # only in non-prod
        return Response(body, status=status.HTTP_202_ACCEPTED)


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
