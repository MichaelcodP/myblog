from rest_framework import serializers
from blog.models import BlogPost, Comment, UserTag


class UserTagSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserTag
        fields = ["id", "user", "user_username", "created_at"]
        read_only_fields = ["created_at"]


class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.PrimaryKeyRelatedField(
        read_only=True
    )  # for create/edit tests (id)
    author_username = serializers.CharField(
        source="author.username", read_only=True
    )  # for filter/search tests
    tagged_users = UserTagSerializer(source="usertags", many=True, read_only=True)
    tagged_count = serializers.SerializerMethodField()
    last_tag_date = serializers.SerializerMethodField()

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
            "tagged_users",
            "tagged_count",
            "last_tag_date",
        ]
        read_only_fields = [
            "author",
            "created_at",
            "updated_at",
            "tagged_count",
            "last_tag_date",
        ]

    def get_tagged_count(self, obj):
        return obj.usertags.count()

    def get_last_tag_date(self, obj):
        last_tag = obj.usertags.order_by("-created_at").first()
        return last_tag.created_at if last_tag else None


class CommentPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "body", "blogpost", "author", "created_at"]
        read_only_fields = ["author", "created_at"]


class BlogPostGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPost
        fields = ["id", "title"]


class CommentGetSerializer(serializers.ModelSerializer):
    blogpost = BlogPostGetSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "body", "blogpost", "author", "created_at"]
