import pytest
from django.contrib.auth.models import User
from blog.models import BlogPost
from django.core.exceptions import ValidationError
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory

# -------------- Factories -----------------


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = Faker('user_name')


class BlogPostFactory(DjangoModelFactory):
    class Meta:
        model = BlogPost

    title = Faker('sentence', nb_words=4)
    body = Faker('text', max_nb_chars=200)
    author = SubFactory(UserFactory)
# -------------- Tests -----------------


@pytest.mark.django_db
class TestBlogPostModel:
    def test_title_cannot_be_empty(self):
        user = UserFactory()
        post = BlogPost(title='', body='Valid body', author=user)
        # Validation via full_clean() raises ValidationError for empty title
        with pytest.raises(ValidationError):
            post.full_clean()

    def test_body_cannot_be_empty(self):
        user = UserFactory()
        post = BlogPost(title='Valid title', body='', author=user)
        # Validation via full_clean() raises ValidationError for empty body
        with pytest.raises(ValidationError):
            post.full_clean()

    def test_author_cannot_be_empty(self):
        post = BlogPost(title='Valid title', body='Valid body', author=None)
        # Validation via full_clean() raises ValidationError for empty author
        with pytest.raises(ValidationError):
            post.full_clean()

    def test_title_max_length(self):
        """Title cannot be longer than 100 characters"""
        user = UserFactory()
        too_long_title = "a" * 101  # Assuming max_length is 100
        post = BlogPost(title=too_long_title, body='Valid body', author=user)
        # Validation via full_clean() raises ValidationError for title exceeding max_length
        with pytest.raises(ValidationError):
            post.full_clean()

    def test_body_max_length(self):
        """Body cannot be longer than 255 characters"""
        user = UserFactory()
        too_long_body = "a" * 256  # Assuming max_length is 255
        post = BlogPost(title='Valid title', body=too_long_body, author=user)
        # Validation via full_clean() raises ValidationError for body exceeding max_length
        with pytest.raises(ValidationError):
            post.full_clean()

    def test_cascade_delete_author(self):
        """Posts are deleted along with the author"""
        user = UserFactory()
        BlogPostFactory(author=user)
        assert BlogPost.objects.filter(author=user).count() == 1
        user_id = user.id
        user.delete()
        assert BlogPost.objects.filter(author=user_id).count() == 0

    def test_create_valid_happy_path(self):
        """Successful creation of post"""
        user = UserFactory()
        post = BlogPost.objects.create(
            title='A valid title',
            body='A valid body',
            author=user
        )
        assert BlogPost.objects.count() == 1
        assert post.title == 'A valid title'
        assert post.body == 'A valid body'
        assert post.author == user