"""Persistence layer for storing OAuth connections per user."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.database.models import User
from app.database.session import get_session
from app.schemas.auth import ConnectionStatus, PlatformConnectionsStatus


DEFAULT_USER_EMAIL = getattr(settings, "DEFAULT_USER_EMAIL", None) or "default@socialamplifier.local"


class UserConnectionService:
    """Handle persistence of OAuth tokens and connection state."""

    def __init__(self, default_email: str = DEFAULT_USER_EMAIL) -> None:
        self.default_email = default_email

    async def update_linkedin_connection(
        self,
        tokens: Dict[str, Any],
        expires_at: Optional[datetime],
        username: Optional[str],
        member_id: Optional[str],
    ) -> ConnectionStatus:
        async with get_session() as session:
            user = await self._ensure_user(session)
            user.linkedin_access_token = tokens.get("access_token")
            user.linkedin_refresh_token = tokens.get("refresh_token")
            user.linkedin_token_expires = expires_at
            user.linkedin_connected = True
            user.linkedin_username = username
            user.linkedin_user_id = member_id
            user.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(user)

            return self._build_connection_status("linkedin", user)

    async def update_twitter_connection(
        self,
        tokens: Dict[str, Any],
        expires_at: Optional[datetime],
        username: Optional[str],
        user_id: Optional[str],
    ) -> ConnectionStatus:
        async with get_session() as session:
            user = await self._ensure_user(session)
            user.twitter_access_token = tokens.get("access_token")
            user.twitter_refresh_token = tokens.get("refresh_token")
            user.twitter_token_expires = expires_at
            user.twitter_connected = True
            user.twitter_username = username
            user.twitter_user_id = user_id
            user.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(user)

            return self._build_connection_status("twitter", user)

    async def get_connection_status(self) -> PlatformConnectionsStatus:
        async with get_session() as session:
            user = await self._ensure_user(session)

            return PlatformConnectionsStatus(
                linkedin=self._build_connection_status("linkedin", user),
                twitter=self._build_connection_status("twitter", user),
            )

    async def disconnect(self, platform: str) -> ConnectionStatus:
        async with get_session() as session:
            user = await self._ensure_user(session)

            if platform == "linkedin":
                user.linkedin_access_token = None
                user.linkedin_refresh_token = None
                user.linkedin_token_expires = None
                user.linkedin_connected = False
                user.linkedin_username = None
                user.linkedin_user_id = None
            elif platform == "twitter":
                user.twitter_access_token = None
                user.twitter_refresh_token = None
                user.twitter_token_expires = None
                user.twitter_connected = False
                user.twitter_username = None
                user.twitter_user_id = None
            else:  # pragma: no cover - validation handled at route level
                raise ValueError(f"Unsupported platform: {platform}")

            user.updated_at = datetime.utcnow()

            await session.commit()
            await session.refresh(user)

            return self._build_connection_status(platform, user)

    async def _ensure_user(self, session: AsyncSession) -> User:
        stmt = select(User).where(User.email == self.default_email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()

        if not user:
            user = User(email=self.default_email)
            session.add(user)
            await session.commit()
            await session.refresh(user)

        return user

    def _build_connection_status(self, platform: str, user: User) -> ConnectionStatus:
        now = datetime.utcnow()

        if platform == "linkedin":
            expires_at = user.linkedin_token_expires
            connected = bool(
                user.linkedin_connected
                and user.linkedin_access_token
                and (expires_at is None or expires_at > now)
            )

            if not connected:
                return ConnectionStatus(
                    platform="linkedin",
                    connected=False,
                    expires_at=None,
                    username=None,
                )

            return ConnectionStatus(
                platform="linkedin",
                connected=True,
                expires_at=expires_at,
                username=user.linkedin_username,
            )

        if platform == "twitter":
            expires_at = user.twitter_token_expires
            connected = bool(
                user.twitter_connected
                and user.twitter_access_token
                and (expires_at is None or expires_at > now)
            )

            if not connected:
                return ConnectionStatus(
                    platform="twitter",
                    connected=False,
                    expires_at=None,
                    username=None,
                )

            return ConnectionStatus(
                platform="twitter",
                connected=True,
                expires_at=expires_at,
                username=user.twitter_username,
            )

        raise ValueError(f"Unsupported platform: {platform}")


user_connection_service = UserConnectionService()
