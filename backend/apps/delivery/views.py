from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import serializers as drf_s

from apps.accounts.permissions import IsKYCVerified

from .models import DeliveryRequest
from .services import request_delivery


class DeliveryRequestSerializer(drf_s.ModelSerializer):
    class Meta:
        model = DeliveryRequest
        fields = "__all__"
        read_only_fields = [
            "id", "state", "processing_fee_rial", "tracking_code",
            "created_at", "updated_at", "user",
        ]


class DeliveryListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = DeliveryRequestSerializer

    def get_queryset(self):
        return DeliveryRequest.objects.filter(user=self.request.user).order_by("-created_at")


class DeliveryCreateView(APIView):
    permission_classes = [IsAuthenticated, IsKYCVerified]

    def post(self, request):
        try:
            mg = int(request.data.get("requested_mg", 0))
        except (TypeError, ValueError):
            return Response({"detail": "وزن نامعتبر"}, status=400)
        try:
            req = request_delivery(
                user=request.user, mg=mg,
                address=request.data.get("shipping_address", ""),
                name=request.data.get("recipient_name", ""),
                nid=request.data.get("recipient_national_id", ""),
                phone=request.data.get("recipient_phone", ""),
                bars=request.data.get("bars_breakdown") or {},
            )
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=400)
        return Response(DeliveryRequestSerializer(req).data, status=status.HTTP_201_CREATED)
