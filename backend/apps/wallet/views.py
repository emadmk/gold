"""Wallet API views."""
from __future__ import annotations

from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsKYCVerified

from .models import WalletTransaction
from .serializers import (
    GoldWalletSerializer,
    RialWalletSerializer,
    WalletTransactionSerializer,
)
from .services import InsufficientFunds, ensure_wallets


class WalletOverviewView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rial, gold = ensure_wallets(request.user)
        return Response({
            "rial": RialWalletSerializer(rial).data,
            "gold": GoldWalletSerializer(gold).data,
        })


class WalletTransactionListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = WalletTransactionSerializer

    def get_queryset(self):
        return WalletTransaction.objects.filter(user=self.request.user).order_by("-created_at")


class WithdrawRequestView(APIView):
    """Withdraw rial — requires KYC + OTP."""

    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
        from apps.accounts.services import otp as otp_svc
        from .services import debit_rial

        try:
            amount = int(request.data.get("amount_rial", 0))
        except (TypeError, ValueError):
            return Response({"detail": "مبلغ نامعتبر است."}, status=400)
        if amount < 100_000:
            return Response({"detail": "حداقل مبلغ برداشت ۱۰۰,۰۰۰ ریال است."}, status=400)
        code = request.data.get("otp", "")
        if not otp_svc.verify_otp(request.user.phone, code, purpose="withdraw"):
            return Response({"detail": "کد یکبارمصرف معتبر نیست."}, status=400)
        debit_rial(request.user, amount, kind="withdraw",
                   description="درخواست برداشت ریالی")
        return Response({"detail": "درخواست برداشت ثبت شد. حداکثر ۳ روز کاری."},
                        status=status.HTTP_201_CREATED)


class WithdrawOTPRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from apps.accounts.services import otp as otp_svc

        otp_svc.request_otp(request.user.phone, purpose="withdraw")
        return Response({"detail": "کد تأیید برداشت ارسال شد."})


class TransferOTPRequestView(APIView):
    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
        from apps.accounts.services import otp as otp_svc

        otp_svc.request_otp(request.user.phone, purpose="transfer")
        return Response({"detail": "کد تأیید انتقال ارسال شد."})


class TransferView(APIView):
    """Transfer gold/silver to another wallet by address. OTP-gated."""

    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
        from .transfer import transfer

        asset = request.data.get("asset", "gold")
        try:
            mg = int(request.data.get("mg", 0))
        except (TypeError, ValueError):
            return Response({"detail": "مقدار نامعتبر است."}, status=400)
        address = request.data.get("to_address", "")
        otp = request.data.get("otp", "")
        try:
            out, _ = transfer(
                sender=request.user, recipient_address=address,
                asset=asset, mg=mg, otp_code=otp,
            )
        except (ValueError, InsufficientFunds, PermissionError) as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(WalletTransactionSerializer(out).data, status=status.HTTP_201_CREATED)
