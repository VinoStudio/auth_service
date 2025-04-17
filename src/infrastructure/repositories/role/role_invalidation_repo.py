from dataclasses import dataclass
from datetime import datetime, UTC

from src.infrastructure.repositories import RedisRepository


@dataclass
class RoleInvalidationRepository(RedisRepository):
    prefix = "invalid_role: "

    async def invalidate_role(
        self, role_name: str, expiration_duration: float | None = None
    ) -> bool:
        """
        Invalidate a role by storing the current timestamp with microseconds

        Args:
            role_name: The name of the role to invalidate
            expiration_duration: How long to keep this record in Redis (in seconds)
                                 Defaults to 8 days if None

        Returns:
            bool: Whether the operation was successful
        """
        # Default to 8 days if no expiration is provided
        if expiration_duration is None:
            expiration_duration = 60 * 60 * 24 * 8  # 8 days in seconds

        key = f"{self.prefix}{role_name}"
        # Get current timestamp with microseconds
        value = str(datetime.now(UTC).timestamp())

        return await self.set(key=key, value=value, expire=expiration_duration)

    async def get_role_invalidation_time(self, role_name: str) -> str | None:
        """
        Get the invalidation timestamp for a role if it exists

        Args:
            role_name: The name of the role to check

        Returns:
            str | None: The timestamp when the role was invalidated, or None if not invalidated
        """
        key = f"{self.prefix}{role_name}"

        return await self.get(key=key)
