from dataclasses import dataclass
from datetime import datetime, UTC

from src.infrastructure.repositories import RedisRepository


# @dataclass
# class RoleInvalidationRepository(RedisRepository):
#     """Repository for managing role invalidations in Redis"""
#
#     map_key = "role_invalidations"  # Hash key for all role invalidations
#     expiration_days = 7
#
#     async def invalidate_role(self, role_name: str) -> bool:
#         """
#         Mark a role as invalidated at the current timestamp
#         Returns True if successful
#         """
#         timestamp = str(datetime.now(UTC).timestamp())
#
#         async with self.redis.client() as client:
#             # Add role to invalidation map
#             await client.hset(self.map_key, role_name, timestamp)
#             # Reset expiration time on the whole map
#             await client.expire(self.map_key, 60 * 60 * 24 * self.expiration_days)
#             return True
#
#     async def get_all_role_invalidations(self) -> dict[str, float]:
#         """
#         Get all role invalidation timestamps as a dictionary
#         Returns {role_name: timestamp} mapping
#         """
#         async with self.redis.client() as client:
#             result = await client.hgetall(self.map_key)
#             if not result:
#                 return {}
#
#             # Convert bytes keys/values to string/float
#             return {
#                 k.decode("utf-8"): float(v.decode("utf-8")) for k, v in result.items()
#             }
#
#     async def is_role_invalidated_after(self, role_name: str, issued_at: float) -> bool:
#         """
#         Check if a specific role was invalidated after the given timestamp
#         Returns True if the role was invalidated after issued_at
#         """
#         async with self.redis.client() as client:
#             invalidated_at = await client.hget(self.map_key, role_name)
#             if not invalidated_at:
#                 return False
#
#             invalidated_timestamp = float(invalidated_at.decode("utf-8"))
#             return invalidated_timestamp > issued_at
#
#     async def are_any_roles_invalidated_after(
#         self, roles: list[str], issued_at: float
#     ) -> bool:
#         """
#         Check if any of the given roles were invalidated after the given timestamp
#         Returns True if any role was invalidated after issued_at
#         """
#         invalidations = await self.get_all_role_invalidations()
#
#         for role in roles:
#             if role in invalidations and invalidations[role] > issued_at:
#                 return True
#
#         return False


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
