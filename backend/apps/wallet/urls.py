from django.urls import path

from .views import (
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
]
