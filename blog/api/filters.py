import django_filters
from blog.models import BlogPost


class BlogPostFilter(django_filters.FilterSet):
    created_at = django_filters.IsoDateTimeFilter(
        field_name="created_at", lookup_expr="gte"
    )
    created_at_before = django_filters.IsoDateTimeFilter(
        field_name="created_at", lookup_expr="lte"
    )

    class Meta:
        model = BlogPost
        fields = [
            "safe_for_work",
            "author",
        ]
