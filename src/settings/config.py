from pydantic_settings import BaseSettings
from dataclasses import dataclass
from pydantic import Field, EmailStr
from dishka import provide, Scope, Provider


class JWTSettings(BaseSettings):
    secret_key: str = Field(default="secret_key", alias="JWT_SECRET_KEY")
    access_token_expire_minutes: int = 60 * 24
    refresh_token_expire_minutes: int = 60 * 24 * 7
    verify_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    httponly: bool = True
    secure: bool = True
    samesite: str = "Lax"
    cookie_path: str = "/"


# class SMTPSettings(BaseSettings):
#     host: str = Field()
#     port: int = config.SMTP_PORT
#     user: EmailStr = config.SMTP_USER
#     password: str = config.SMTP_PASS
#
#     @property
#     def url(self):
#         return f"smtp://{self.user}:{self.password}@{self.host}:{self.port}"


class RedisSettings(BaseSettings):
    host: str = Field(default="localhost", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")

    @property
    def redis_url(self):
        return f"redis://{self.host}:{self.port}/0"


class PostgresDB(BaseSettings):
    db_name: str = Field(default="postgres", alias="POSTGRES_DB")
    db_host: str = Field(default="localhost", alias="POSTGRES_HOST")
    db_port: str = Field(default="5435", alias="POSTGRES_PORT")
    db_user: str = Field(default="postgres", alias="POSTGRES_USER")
    db_password: str = Field(default="postgres", alias="POSTGRES_PASSWORD")

    class Config:
        env_prefix = "POSTGRES_"
        case_sensitive = False

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class TestPostgresDB(BaseSettings):
    db_name: str = Field(default="postgres_test", alias="POSTGRES_TEST_DB")
    db_host: str = Field(default="localhost", alias="POSTGRES_TEST_HOST")
    db_port: str = Field(default="5436", alias="POSTGRES_TEST_PORT")
    db_user: str = Field(default="postgres_test", alias="POSTGRES_TEST_USER")
    db_password: str = Field(default="postgres_test", alias="POSTGRES_PASSWORD")

    class Config:
        env_prefix = "POSTGRES_"
        case_sensitive = False

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"


class KafkaConfig(BaseSettings):
    kafka_url: str = Field(default="kafka:29092", alias="KAFKA_URL")
    user_service_topic: str = Field(default="user_service_topic")

    class Config:
        env_prefix = "KAFKA_"
        case_sensitive = False


@dataclass(frozen=True)
class Config:
    postgres = PostgresDB()
    test_db = TestPostgresDB()
    kafka = KafkaConfig()
    redis = RedisSettings()
    jwt = JWTSettings()
    # smtp = SMTPSettings()


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_config(self) -> Config:
        return Config()
