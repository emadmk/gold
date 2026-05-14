from django.urls import path

from .views import (
    BuyGoldView,
    BuySilverView,
    CancelOrderView,
    OrderDetailView,
    OrderInvoiceView,
    OrderListView,
    SellGoldView,
    SellSilverView,
)

urlpatterns = [
    path("orders", OrderListView.as_view()),
    path("orders/<uuid:id>", OrderDetailView.as_view()),
    path("orders/<uuid:id>/cancel", CancelOrderView.as_view()),
    path("orders/<uuid:id>/invoice", OrderInvoiceView.as_view()),
    path("trade/buy/gold", BuyGoldView.as_view()),
    path("trade/sell/gold", SellGoldView.as_view()),
    path("trade/buy/silver", BuySilverView.as_view()),
    path("trade/sell/silver", SellSilverView.as_view()),
]
