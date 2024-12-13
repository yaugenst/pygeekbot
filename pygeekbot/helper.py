"""Helper methods built on top of the Geekbot API."""

from typing import List, Optional, TypeVar
from .models import (
    Standup,
    StandupReport,
    StandupUser,
    StandupUpdate,
)

T = TypeVar("T", bound="GeekbotHelperMixin")


class GeekbotHelperMixin:
    """Helper methods built on top of the base API methods."""

    async def get_user_reports(
        self,
        user_id: int,
        limit: int = 30,
        after: Optional[int] = None,
        before: Optional[int] = None,
    ) -> List[StandupReport]:
        """Get reports for a specific user."""
        return await self.get_reports(
            user_id=user_id, limit=limit, after=after, before=before
        )

    async def get_standup_reports_since(
        self,
        standup_id: int,
        since_timestamp: int,
        limit: int = 100,
    ) -> List[StandupReport]:
        """Get all reports for a standup since a specific time."""
        return await self.get_reports(
            standup_id=standup_id, after=since_timestamp, limit=limit
        )

    async def find_standup_by_name(self: T, name: str) -> Optional[Standup]:
        """Find a standup by its name (case-insensitive)."""
        standups = await self.get_standups()
        return next((s for s in standups if s.name.lower() == name.lower()), None)

    async def clone_standup(
        self,
        standup_id: int,
        new_name: str,
        new_channel: Optional[str] = None,
    ) -> Standup:
        """Clone a standup with minimal changes."""
        return await self.duplicate_standup(
            standup_id=standup_id, name=new_name, channel=new_channel
        )

    async def pause_standup(self, standup_id: int) -> Standup:
        """Pause a standup by setting wait_time to null."""
        return await self.update_standup(standup_id, StandupUpdate(wait_time=None))

    async def find_user_by_email(self, email: str) -> Optional[StandupUser]:
        """Find a team member by their email."""
        team = await self.get_team()
        return next((u for u in team.users if u.email.lower() == email.lower()), None)

    async def get_user_standups(self, user_id: int) -> List[Standup]:
        """Get all standups that a user participates in."""
        standups = await self.get_standups()
        return [s for s in standups if any(u.id == str(user_id) for u in s.users)]

    @staticmethod
    def format_time(hour: int, minute: int = 0) -> str:
        """Format time in HH:MM:SS format."""
        return f"{hour:02d}:{minute:02d}:00"

    @staticmethod
    def weekday_to_str(day: int) -> str:
        """Convert weekday number (0-6) to three-letter format (Mon-Sun)."""
        days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        return days[day]

    async def get_all_reports(
        self: T,
        standup_id: Optional[int] = None,
        user_id: Optional[int] = None,
        after: Optional[int] = None,
        before: Optional[int] = None,
    ) -> List[StandupReport]:
        """Get all reports, handling pagination automatically."""
        all_reports = []
        limit = 100  # Maximum allowed by API

        while True:
            batch = await self.get_reports(
                standup_id=standup_id,
                user_id=user_id,
                after=after,
                before=before,
                limit=limit,
            )
            if not batch:
                break

            all_reports.extend(batch)
            if len(batch) < limit:
                break

            # Update after parameter for next batch
            after = max(r.timestamp for r in batch if r.timestamp is not None)

        return all_reports
