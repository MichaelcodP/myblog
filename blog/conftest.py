import pytest
from unittest.mock import MagicMock, patch


@pytest.fixture(autouse=True)
def mock_redis():
    # Replaces redis.Redis in all tests so that it does not connect for real
    with patch("blog.utils.redis.Redis", return_value=MagicMock()) as mock:
        yield mock
