# from django.test import TestCase
# from django.db.utils import IntegrityError
import pytest
from django.contrib.auth.models import User
from blog.models import BlogPost
from django.core.exceptions import ValidationError

# import factory
from factory.django import DjangoModelFactory
from factory import Faker, SubFactory

# Create your tests here.
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
