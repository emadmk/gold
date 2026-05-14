from django.urls import path

from .views import AdminKPIView

urlpatterns = [
    path("admin/kpi", AdminKPIView.as_view()),
]
