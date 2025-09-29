from rest_framework import serializers
from blog.models import BlogPost


class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(slug_field="username", read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "body",
            "author",
            "created_at",
            "updated_at",
            "safe_for_work",
        ]
        read_only_fields = ["author", "created_at", "updated_at"]
