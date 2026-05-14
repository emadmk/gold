from __future__ import annotations

from django.db.models import F
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Post
from .serializers import PostDetailSerializer, PostListSerializer


class PostListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = PostListSerializer
    queryset = Post.objects.filter(state="published").select_related("category", "author")


class PostDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = PostDetailSerializer
    queryset = Post.objects.filter(state="published")
    lookup_field = "slug"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Post.objects.filter(pk=instance.pk).update(views=F("views") + 1)
        return super().retrieve(request, *args, **kwargs)
