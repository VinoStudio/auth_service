from dataclasses import dataclass
from datetime import datetime, UTC

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
            return value.decode("utf-8") or None

    async def delete(self, key: str) -> None:
        async with self.redis.client() as client:
            await client.delete(key)

    async def exists(self, key: str) -> bool:
        async with self.redis.client() as client:
            return await client.exists(key) > 0


class TokenBlackListRepository(RedisRepository):
    prefix = "revoked_user: "

    async def add_to_blacklist(self, user_id: str, expires_in_seconds: int) -> bool:
        """
        If user is banned, deleted or permissions changed:
        add a user_id to the blacklist with an expiration time to prevent any future access
        """

        key = f"{self.prefix}{user_id}"
        value = str(datetime.now(UTC))
        return await self.set(key=key, value=value, expire=expires_in_seconds)

    async def get_from_blacklist(self, user_id: str) -> str | None:
        """Check if a session is blacklisted"""
        key = f"{self.prefix}{user_id}"

        return await self.get(key=key)
