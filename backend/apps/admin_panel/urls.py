from django.urls import path

from .views import (
    AdminAuditLogView,
    AdminDeliveryActionView,
    AdminDeliveryView,
    AdminFormulasView,
    AdminKPIView,
    AdminKYCQueueView,
    AdminOrdersView,
    AdminPaymentsView,
    AdminSettlementsView,
    AdminUsersView,
    AdminVendorsView,
    FreezeUserView,
    UnfreezeUserView,
)

urlpatterns = [
    path("admin/kpi", AdminKPIView.as_view()),
    path("admin/kyc-queue", AdminKYCQueueView.as_view()),
    path("admin/users", AdminUsersView.as_view()),
    path("admin/users/<uuid:user_id>/freeze", FreezeUserView.as_view()),
    path("admin/users/<uuid:user_id>/unfreeze", UnfreezeUserView.as_view()),
    path("admin/vendors-list", AdminVendorsView.as_view()),
    path("admin/orders", AdminOrdersView.as_view()),
    path("admin/payments", AdminPaymentsView.as_view()),
    path("admin/delivery", AdminDeliveryView.as_view()),
    path("admin/delivery/<uuid:delivery_id>/<str:action>", AdminDeliveryActionView.as_view()),
    path("admin/formulas", AdminFormulasView.as_view()),
    path("admin/settlements", AdminSettlementsView.as_view()),
    path("admin/audit-log", AdminAuditLogView.as_view()),
]
