from __future__ import annotations

from rest_framework import generics, serializers as drf_s
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification


class NotificationSerializer(drf_s.ModelSerializer):
    class Meta:
        model = Notification
        fields = ["id", "kind", "title", "body", "url", "read", "metadata", "created_at"]


class NotificationListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by("-created_at")


class NotificationMarkReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, notif_id: str):
        n = Notification.objects.filter(user=request.user, id=notif_id).update(read=True)
        return Response({"updated": n})


class NotificationMarkAllReadView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        n = Notification.objects.filter(user=request.user, read=False).update(read=True)
        return Response({"updated": n})
