from django.urls import path

from .views import DeliveryCreateView, DeliveryListView

urlpatterns = [
    path("delivery", DeliveryListView.as_view()),
    path("delivery/request", DeliveryCreateView.as_view()),
]
