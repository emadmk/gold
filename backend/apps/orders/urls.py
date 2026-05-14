from django.urls import path

from .views import BuyGoldView, CancelOrderView, OrderDetailView, OrderListView, SellGoldView

urlpatterns = [
    path("orders", OrderListView.as_view()),
    path("orders/<uuid:id>", OrderDetailView.as_view()),
    path("orders/<uuid:id>/cancel", CancelOrderView.as_view()),
    path("trade/buy/gold", BuyGoldView.as_view()),
    path("trade/sell/gold", SellGoldView.as_view()),
]
