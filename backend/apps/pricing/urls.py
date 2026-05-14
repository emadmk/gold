from django.urls import path

from .views import LivePricesView, QuoteView

urlpatterns = [
    path("prices", LivePricesView.as_view()),
    path("prices/quote", QuoteView.as_view()),
]
