import os
import random
import string


class Settings:
    jwt_secret: str
    access_token_lifetime: int = 5 * 60
    db_url: str = "postgresql://postgres:postgres@localhost:5432/postgres"

    def __init__(self) -> None:
        if self.is_env_var_set("DEV"):
            self.access_token_lifetime = 60 * 60
            self.jwt_secret = "dev_secret"
        elif self.is_env_var_set("TESTING"):
            self.access_token_lifetime = 60 * 60
            self.jwt_secret = "testing_secret"
            self.db_url = "postgresql://testing:testing@localhost:5433/testing"
        else:
            self.jwt_secret = "".join(random.choice(string.ascii_letters + string.digits) for i in range(12))

    @staticmethod
    def is_env_var_set(env_var: str) -> bool:
        return os.getenv(env_var, "0") == "1"


settings = Settings()
