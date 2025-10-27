import logging
from rest_framework import serializers
from blog.models import BlogPost, Comment, UserTag
from blog.utils import get_redis_connection

logger = logging.getLogger(__name__)


class UserTagSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source="user.username", read_only=True)

    class Meta:
        model = UserTag
        fields = ["id", "user", "user_username", "created_at"]
        read_only_fields = ["created_at"]


class BlogPostSerializer(serializers.ModelSerializer):
    """
    Serializer for blog posts.

    Fields:
    - title: The title of the blog post
    - body: The main content
    - author: User who created the post
    - created_at: DateTime when post was created
    """

    author = serializers.PrimaryKeyRelatedField(
        read_only=True
    )  # for create/edit tests (id)
    author_username = serializers.CharField(
        source="author.username", read_only=True
    )  # for filter/search tests
    tagged_users = UserTagSerializer(source="usertags", many=True, read_only=True)
    tagged_count = serializers.SerializerMethodField()
    last_tag_date = serializers.SerializerMethodField()

    visits_count = serializers.SerializerMethodField()

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
            "visits_count",
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

    def get_visits_count(self, obj):
        try:
            redis_client = get_redis_connection()
            count = redis_client.get(f"post:{obj.pk}:visits")
            return int(count) if count else 0
        except Exception as e:
            logger.error(
                f"Redis connection failed in get_visits_count for post {obj.pk}: {e}"
            )
            return 0


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
