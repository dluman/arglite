import pytest

from arglite import Parser


@pytest.fixture
def parser():
    """Return a fresh Parser instance for each test."""
    return Parser()
