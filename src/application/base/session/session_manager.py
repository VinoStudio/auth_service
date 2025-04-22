from abc import ABC, abstractmethod
from typing import Any, Optional, List
from src.application.base.interface.request import RequestProtocol

import src.domain as domain


class BaseSessionManager(ABC):
    """
    Manages user sessions across different devices.

    This class handles session lifecycle including creation, retrieval, updates,
    and deactivation. It tracks user activity across multiple devices and provides
    methods to manage session state.
    """

    @abstractmethod
    async def get_or_create_session(
        self, user_id: str, request: RequestProtocol
    ) -> Optional[domain.Session]:
        """
        Get an existing session for the user and device or create a new one.

        Examines the request to identify the device, then either returns an
        existing active session or creates a new one if none exists.

        Args:
            user_id: The unique identifier of the user
            request: The HTTP request containing device information

        Returns:
            domain.Session: The existing or newly created session

        Note:
            If an existing session is found, its activity timestamp is updated
        """

        raise NotImplementedError

    @abstractmethod
    async def get_user_session(
        self, user_id: str, device_id: str
    ) -> Optional[domain.Session]:
        """
        Get an active session for a specific user and device.

        Retrieves an active session if one exists and updates its last
        activity timestamp.

        Args:
            user_id: The unique identifier of the user
            device_id: The unique identifier of the device

        Returns:
            Optional[domain.Session]: The active session if found, otherwise None
        """
        raise NotImplementedError

    @abstractmethod
    async def deactivate_user_session(self, user_id: str, device_id: str) -> None:
        """
        Deactivate a session for a specific user and device.

        Marks the session as inactive, effectively logging the user out
        from the specified device.

        Args:
            user_id: The unique identifier of the user
            device_id: The unique identifier of the device
        """
        raise NotImplementedError

    @abstractmethod
    async def deactivate_session(self, session_id: str) -> None:
        """
        Deactivate a session by its unique identifier.

        Marks the session as inactive, effectively ending the user's session.

        Args:
            session_id: The unique identifier of the session to deactivate
        """
        raise NotImplementedError

    @abstractmethod
    async def deactivate_all_user_sessions(self, user_id: str) -> None:
        """
        Deactivate all active sessions for a specific user.

        Marks all of a user's sessions as inactive, effectively logging the user
        out from all devices.

        Args:
            user_id: The unique identifier of the user
        """
        raise NotImplementedError

    @abstractmethod
    async def update_session_activity(self, session_id: str) -> None:
        """
        Update the last activity timestamp for a session.

        Refreshes the session's last activity time to the current time.

        Args:
            session_id: The unique identifier of the session to update
        """
        raise NotImplementedError

    @abstractmethod
    async def get_user_active_sessions(self, user_id: str) -> List[domain.Session]:
        """
        Get all active sessions for a specific user.

        Retrieves all currently active sessions across all devices
        for the specified user.

        Args:
            user_id: The unique identifier of the user

        Returns:
            List[domain.Session]: List of all active sessions for the user
        """
        raise NotImplementedError
