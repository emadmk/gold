from django.urls import path

from .views import PaymentCallbackView, TopupRequestView

urlpatterns = [
    path("wallet/topup", TopupRequestView.as_view()),
    path("payments/callback/<str:gateway>", PaymentCallbackView.as_view()),
]
