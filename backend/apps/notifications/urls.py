from django.urls import path

from .views import (
    NotificationListView,
    NotificationMarkAllReadView,
    NotificationMarkReadView,
)

urlpatterns = [
    path("notifications", NotificationListView.as_view()),
    path("notifications/<uuid:notif_id>/read", NotificationMarkReadView.as_view()),
    path("notifications/read-all", NotificationMarkAllReadView.as_view()),
]
