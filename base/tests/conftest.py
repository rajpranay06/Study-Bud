import pytest
from django.conf import settings

@pytest.fixture(scope="session")
def django_db_setup():
    """
    Fixture to configure the DB connection
    This prevents Django from running migrations when running tests
    """
    settings.DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
        "ATOMIC_REQUESTS": False,
    } 