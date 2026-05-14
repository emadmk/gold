from rest_framework import serializers

from .models import Category, Post, Tag


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ["code", "title_fa"]


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ["code", "title_fa"]


class PostListSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    author = serializers.SerializerMethodField()

    class Meta:
        model = Post
        fields = ["id", "slug", "title", "summary", "cover_image",
                  "category", "tags", "author", "published_at", "views"]

    def get_author(self, obj):
        return obj.author.full_name


class PostDetailSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ["body_md"]
