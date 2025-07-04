import os
import uuid

from config import get_config, get_db_url


class TestGetDbUrl:
    def test__when_not_in_debug__then_postgres_url_returned(self):
        os.environ["FLASK_DEBUG"] = ""
        assert get_db_url() == "postgresql://postgres@/postgres"
        del os.environ["FLASK_DEBUG"]

    def test__when_in_debug__then_postgres_url_returned(self):
        os.environ["FLASK_DEBUG"] = "1"
        assert get_db_url() == "postgresql://postgres:postgres@localhost:5432/postgres"
        del os.environ["FLASK_DEBUG"]


class TestGetConfig:
    def test__when_flask_debug__then_dev_secret_key_used(self):
        os.environ["FLASK_DEBUG"] = "1"
        config = get_config()
        assert config.SECRET_KEY == "A_KEY_ONLY_USED_FOR_DEV"
        assert config.JWT_ACCESS_TOKEN_EXPIRES == 3600
        del os.environ["FLASK_DEBUG"]

    def test__when_not_flask_debug__then_random_secret_key_used(self):
        os.environ["FLASK_DEBUG"] = ""
        config = get_config()
        assert uuid.UUID(config.SECRET_KEY)
        assert config.JWT_ACCESS_TOKEN_EXPIRES == 300
        del os.environ["FLASK_DEBUG"]
