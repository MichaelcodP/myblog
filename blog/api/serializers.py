from rest_framework import serializers
from blog.models import BlogPost


class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        read_only=True
    )  # for create/edit tests (id)
    author_username = serializers.CharField(
        source="author.username", read_only=True
    )  # for filter/search tests

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "body",
            "author",
            "author_username",
            "created_at",
            "updated_at",
            "safe_for_work",
            "img",
            # "tagged_count",
            # "last_tag_date",
        ]
        read_only_fields = [
            "author",
            "created_at",
            "updated_at",
            "tagged_count",
            "last_tag_date",
        ]
