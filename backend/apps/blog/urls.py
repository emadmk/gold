from django.urls import path

from .views import PostDetailView, PostListView

urlpatterns = [
    path("blog/posts", PostListView.as_view()),
    path("blog/posts/<slug:slug>", PostDetailView.as_view()),
]
