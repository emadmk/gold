from rest_framework import generics, serializers as drf_s
from rest_framework.permissions import IsAuthenticated

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
