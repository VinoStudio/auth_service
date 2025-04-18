from abc import ABC, abstractmethod
from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings
from dataclasses import dataclass
from pydantic import Field, EmailStr
from dishka import provide, Scope, Provider


@dataclass
class OAuthProvider(ABC):
    @abstractmethod
    def get_auth_url(self) -> str:
        raise NotImplementedError


class OAuthGoogle(BaseSettings, OAuthProvider):
    name: str = Field(default="google")
    client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")
    redirect_uri: str = Field(
        default="http://localhost:8002/oauth/callback/google",
        alias="GOOGLE_REDIRECT_URI",
    )
    token_url: str = Field(
        default="https://accounts.google.com/o/oauth2/token", alias="GOOGLE_TOKEN_URI"
    )
    userinfo_url: str = Field(
        default="https://openidconnect.googleapis.com/v1/userinfo",
        alias="GOOGLE_USER_INFO_URI",
    )

    def get_auth_url(self) -> str:
        return f"https://accounts.google.com/o/oauth2/v2/auth?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope=openid%20profile%20email&access_type=offline"


class OAuthYandex(BaseSettings, OAuthProvider):
    name: str = Field(default="yandex")
    client_id: str = Field(default="", alias="YANDEX_CLIENT_ID")
    client_secret: str = Field(default="", alias="YANDEX_CLIENT_SECRET")
    redirect_uri: str = Field(
        default="http://localhost:8002/oauth/callback/yandex",
        alias="YANDEX_REDIRECT_URI",
    )
    token_url: str = Field(
        default="https://oauth.yandex.ru/token", alias="YANDEX_TOKEN_URI"
    )
    userinfo_url: str = Field(
        default="https://login.yandex.ru/info", alias="YANDEX_USER_INFO_URI"
    )

    def get_auth_url(self) -> str:
        return f"https://oauth.yandex.ru/authorize?response_type=code&client_id={self.client_id}&redirect_uri={self.redirect_uri}"


class JWTSettings(BaseSettings):
    secret_key: str = Field(default="secret_key", alias="JWT_SECRET_KEY")
    access_token_expire_minutes: int = 60 * 24
    refresh_token_expire_minutes: int = 60 * 24 * 7
    verify_token_expire_minutes: int = 60
    algorithm: str = "HS256"
    httponly: bool = True
    secure: bool = True
    samesite: str = "strict"
    cookie_path: str = "/"


class LoggingSettings(BaseSettings):
    render_json_logs: bool = False
    path: Path | None = None
    level: str = "DEBUG"


class SMTPSettings(BaseSettings):
    host: str = Field(default="", alias="SMTP_HOST")
    port: int = Field(default=587, alias="SMTP_PORT")
    user: str = Field(default="", alias="SMTP_USER")
    password: str = Field(default="", alias="SMTP_PASSWORD")

    @property
    def url(self):
        return f"smtp://{self.user}:{self.password}@{self.host}:{self.port}"


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
    logging = LoggingSettings()
    smtp = SMTPSettings()
    google_oauth = OAuthGoogle()
    yandex_oauth = OAuthYandex()


@lru_cache(maxsize=1)
def get_config() -> Config:
    return Config()


class ConfigProvider(Provider):
    @provide(scope=Scope.APP)
    async def get_config(self) -> Config:
        return Config()
