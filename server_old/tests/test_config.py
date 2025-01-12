import os
import re
from unittest import mock

from config import Config, get_db_url


def test__get_db_url__when_not_in_debug__then_postgres_url_returned():
    os.environ["FLASK_DEBUG"] = ""
    assert get_db_url() == "postgresql://postgres@/postgres"
    del os.environ["FLASK_DEBUG"]


def test__get_db_url__when_in_debug__then_postgres_url_returned():
    os.environ["FLASK_DEBUG"] = "1"
    assert get_db_url() == "postgresql://postgres:postgres@localhost:5432/postgres"
    del os.environ["FLASK_DEBUG"]


def test__Config__when_flask_debug__then_dev_secret_key_used():
    os.environ["FLASK_DEBUG"] = "1"
    config = Config()
    assert config.SECRET_KEY == "A_KEY_ONLY_USED_FOR_DEV"
    assert config.JWT_ACCESS_TOKEN_EXPIRES == 3600
    del os.environ["FLASK_DEBUG"]


def test__Config__when_not_flask_debug__then_random_secret_key_used():
    os.environ["FLASK_DEBUG"] = ""
    config = Config()
    assert re.match(r"^[a-zA-Z\d]{32}$", config.SECRET_KEY)
    assert config.JWT_ACCESS_TOKEN_EXPIRES == 300
    del os.environ["FLASK_DEBUG"]
