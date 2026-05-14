from django.urls import path

from .views import (
    TransferOTPRequestView,
    TransferView,
    WalletOverviewView,
    WalletTransactionListView,
    WithdrawOTPRequestView,
    WithdrawRequestView,
)

urlpatterns = [
    path("wallet", WalletOverviewView.as_view()),
    path("wallet/transactions", WalletTransactionListView.as_view()),
    path("wallet/withdraw", WithdrawRequestView.as_view()),
    path("wallet/withdraw/otp", WithdrawOTPRequestView.as_view()),
    path("wallet/transfer", TransferView.as_view()),
    path("wallet/transfer/otp", TransferOTPRequestView.as_view()),
]
