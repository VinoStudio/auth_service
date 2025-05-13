from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum

from redis.asyncio import Redis

from src.infrastructure.base.repository.base import BaseMemoryRepository


@dataclass
class RedisRepository(BaseMemoryRepository):
    """Repository for managing invalidated tokens in Redis"""

    redis: Redis

    async def set(self, key: str, value: str, expire: int) -> bool:
        async with self.redis.client() as client:
            if expire:
                return await client.setex(key, expire, value)
            return await client.set(key, value)

    async def get(self, key: str) -> str | None:
        async with self.redis.client() as client:
            value = await client.get(key)
            if value is None:
                return None
            return value.decode("utf-8")

    async def delete(self, key: str) -> None:
        async with self.redis.client() as client:
            await client.delete(key)

    async def exists(self, key: str) -> bool:
        async with self.redis.client() as client:
            return await client.exists(key) > 0


class TokenType(Enum):
    PASSWORD_RESET = {
        "token_type": "reset_password_token:",
        "expire": 60 * 15,
    }

    EMAIL_CHANGE = {
        "token_type": "email_change_token:",
        "expire": 60 * 60 * 24,
    }

    OAUTH_CONNECT = {
        "token_type": "oauth_connect_state:",
        "expire": 60 * 10,
    }


class TokenBlackListRepository(RedisRepository):
    prefix = "revoked_user: "

    async def add_to_blacklist(
        self, user_id: str, expiration_duration: float | None = None
    ) -> bool:
        """

        Add a user_id to the blacklist with the current timestamp
        The expiration_duration is how long to keep this record in Redis (in seconds)

        """
        # Default to a longer period (e.g., 7 days) if no expiration is provided
        if expiration_duration is None:
            expiration_duration = 60 * 24 * 7  # 7 days in seconds

        key = f"{self.prefix}{user_id}"
        value = str(datetime.now(UTC).timestamp())

        return await self.set(key=key, value=value, expire=expiration_duration)

    async def get_from_blacklist(self, user_id: str) -> str | None:
        """Check if a session is blacklisted"""
        key = f"{self.prefix}{user_id}"

        return await self.get(key=key)

    async def add_reset_token(
        self, user_id: str, token: str, token_type: TokenType
    ) -> bool:
        token_settings = token_type.value
        key = f"{token_settings['token_type']}{token}"
        return await self.set(key=key, value=user_id, expire=token_settings["expire"])

    async def get_reset_token(self, token: str, token_type: TokenType) -> str | None:
        token_settings = token_type.value

        key = f"{token_settings['token_type']}{token}"
        return await self.get(key=key)

    async def invalidate_reset_token(self, token: str, token_type: TokenType) -> bool:
        token_settings = token_type.value

        key = f"{token_settings['token_type']}{token}"
        await self.delete(key=key)
        return True
