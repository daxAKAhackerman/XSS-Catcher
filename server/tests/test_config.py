import os
import re
from unittest import mock

from config import Config, get_db_url


@mock.patch("config.os.path.exists")
def test__get_db_url__when_sqlite_db_exists__then_sqlite_used(exists_mocker: mock.MagicMock):
    db_url = get_db_url()
    assert db_url.startswith("sqlite:///")
    assert db_url.endswith("/app.db")


def test__get_db_url__when_flask_debug__then_sqlite_used():
    os.environ["FLASK_DEBUG"] = "1"
    db_url = get_db_url()
    assert db_url.startswith("sqlite:///")
    assert db_url.endswith("/app.db")


@mock.patch("builtins.open")
@mock.patch("config.os.path.exists", return_value=False)
def test__get_db_url__when_in_prod__then_postgres_used(exists_mocker: mock.MagicMock, open_mocker: mock.MagicMock):
    os.environ["FLASK_DEBUG"] = ""
    os.environ["POSTGRES_USER"] = "user"
    os.environ["POSTGRES_HOSTNAME"] = "127.0.0.1"
    os.environ["POSTGRES_DB"] = "xss"
    os.environ["POSTGRES_PASSWORD_FILE"] = "/tmp/file.txt"

    open_mocker.return_value.__enter__.return_value.readline.return_value.rstrip.return_value = "pass"

    db_url = get_db_url()
    assert db_url == "postgresql://user:pass@127.0.0.1/xss"


def test__Config__when_flask_debug__then_dev_secret_key_used():
    os.environ["FLASK_DEBUG"] = "1"
    config = Config()
    assert config.SECRET_KEY == "A_KEY_ONLY_USED_FOR_DEV"
    assert config.JWT_ACCESS_TOKEN_EXPIRES == 3600


def test__Config__when_not_flask_debug__then_random_secret_key_used():
    os.environ["FLASK_DEBUG"] = ""
    config = Config()
    assert re.match(r"^[a-zA-Z\d]{32}$", config.SECRET_KEY)
    assert config.JWT_ACCESS_TOKEN_EXPIRES == 300
