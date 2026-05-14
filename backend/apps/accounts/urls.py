from django.urls import path

from .views import (
    KYCAdminApproveView,
    KYCAdminRejectView,
    KYCView,
    LogoutView,
    MeView,
    OTPRequestView,
    OTPVerifyView,
)

urlpatterns = [
    path("auth/otp/request", OTPRequestView.as_view()),
    path("auth/otp/verify", OTPVerifyView.as_view()),
    path("auth/logout", LogoutView.as_view()),
    path("me", MeView.as_view()),
    path("kyc", KYCView.as_view()),
    path("admin/kyc/<uuid:submission_id>/approve", KYCAdminApproveView.as_view()),
    path("admin/kyc/<uuid:submission_id>/reject", KYCAdminRejectView.as_view()),
]
