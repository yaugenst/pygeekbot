"""Geekbot API client."""

import asyncio
from typing import List, Optional, Dict, Any
from .models import (
    Standup,
    StandupReport,
    StandupCreate,
    StandupUpdate,
    ReportCreate,
    Team,
    StandupUser,
)
from .logging import setup_logger


from .api import GeekbotApiClient
from .helper import GeekbotHelperMixin


class GeekbotClientAsync(GeekbotHelperMixin, GeekbotApiClient):
    """Async Geekbot client combining API endpoints with helper methods."""

    pass


class GeekbotClient:
    """
    Client for interacting with the Geekbot API.

    This client provides two categories of methods:
    1. Official API methods that directly implement the Geekbot API endpoints
    2. Extended utility methods that provide additional functionality

    Parameters
    ----------
    api_key : str
        The Geekbot API key for authentication

    Notes
    -----
    Official API documentation: https://geekbot.com/developers/
    """

    def __init__(self, api_key: str):
        self.api_key = api_key
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        self._async_client = GeekbotClientAsync(api_key)
        self.client = self._async_client.client
        self.logger = setup_logger("geekbot.client")

    def __enter__(self):
        self.logger.debug("Entering GeekbotClient context")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Clean up resources when exiting context."""
        self.logger.debug("Exiting GeekbotClient context")
        try:
            self._loop.run_until_complete(self._async_client.client.aclose())
        finally:
            self._loop.close()
            asyncio.set_event_loop(None)

    def close(self):
        """Close the HTTP client."""
        self._loop.run_until_complete(self._async_client.close())
        self._loop.close()

    def _run(self, coro):
        """Run a coroutine in the event loop."""
        return self._loop.run_until_complete(coro)

    def get_standups(self) -> List[Standup]:
        """
        List all standups (Official API endpoint).

        Returns
        -------
        List[Standup]
            List of standup objects

        Notes
        -----
        Official API endpoint: GET /v1/standups
        """
        return self._run(self._async_client.get_standups())

    def get_standup(self, standup_id: int) -> Standup:
        """Get a specific standup by ID."""
        return self._run(self._async_client.get_standup(standup_id))

    def create_standup(self, standup: StandupCreate) -> Standup:
        """Creates a new standup."""
        return self._run(self._async_client.create_standup(standup))

    def update_standup(self, standup_id: int, standup: StandupUpdate) -> Standup:
        """Partially updates a standup."""
        return self._run(self._async_client.update_standup(standup_id, standup))

    def replace_standup(self, standup_id: int, standup: StandupCreate) -> Standup:
        """Fully replaces a standup."""
        return self._run(self._async_client.replace_standup(standup_id, standup))

    def duplicate_standup(
        self,
        standup_id: int,
        name: str,
        channel: Optional[str] = None,
        time: Optional[str] = None,
        timezone: Optional[str] = None,
        wait_time: Optional[int] = None,
        days: Optional[List[str]] = None,
        questions: Optional[List[dict]] = None,
        users: Optional[List[int]] = None,
        sync_channel_members: Optional[bool] = None,
        personalised: Optional[bool] = None,
    ) -> Standup:
        """Duplicates a standup with optional modifications."""
        return self._run(
            self._async_client.duplicate_standup(
                standup_id=standup_id,
                name=name,
                channel=channel,
                time=time,
                timezone=timezone,
                wait_time=wait_time,
                days=days,
                questions=questions,
                users=users,
                sync_channel_members=sync_channel_members,
                personalised=personalised,
            )
        )

    def delete_standup(self, standup_id: int) -> None:
        """Delete a standup."""
        self._run(self._async_client.delete_standup(standup_id))

    def start_standup(
        self,
        standup_id: int,
        user_ids: Optional[List[int]] = None,
        emails: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Start a standup for all or specific users."""
        return self._run(
            self._async_client.start_standup(
                standup_id=standup_id,
                user_ids=user_ids,
                emails=emails,
            )
        )

    def get_reports(
        self,
        standup_id: Optional[int] = None,
        limit: Optional[int] = None,
        user_id: Optional[int] = None,
        after: Optional[int] = None,
        before: Optional[int] = None,
        question_ids: Optional[List[int]] = None,
        html: Optional[bool] = None,
    ) -> List[StandupReport]:
        """Get reports, optionally filtered by various parameters."""
        return self._run(
            self._async_client.get_reports(
                standup_id=standup_id,
                limit=limit,
                user_id=user_id,
                after=after,
                before=before,
                question_ids=question_ids,
                html=html,
            )
        )

    def create_report(self, report: ReportCreate) -> StandupReport:
        """Create a new report."""
        return self._run(self._async_client.create_report(report))

    def get_team(self) -> Team:
        """Get team information."""
        return self._run(self._async_client.get_team())

    # Helper Methods
    def get_user_reports(
        self,
        user_id: int,
        limit: int = 30,
        after: Optional[int] = None,
        before: Optional[int] = None,
    ) -> List[StandupReport]:
        """Get reports for a specific user."""
        return self._run(
            self._async_client.get_user_reports(
                user_id=user_id,
                limit=limit,
                after=after,
                before=before,
            )
        )

    def get_standup_reports_since(
        self,
        standup_id: int,
        since_timestamp: int,
        limit: int = 100,
    ) -> List[StandupReport]:
        """Get all reports for a standup since a specific time."""
        return self._run(
            self._async_client.get_standup_reports_since(
                standup_id=standup_id,
                since_timestamp=since_timestamp,
                limit=limit,
            )
        )

    def find_standup_by_name(self, name: str) -> Optional[Standup]:
        """Find a standup by its name (case-insensitive)."""
        return self._run(self._async_client.find_standup_by_name(name))

    def clone_standup(
        self,
        standup_id: int,
        new_name: str,
        new_channel: Optional[str] = None,
    ) -> Standup:
        """Clone a standup with minimal changes."""
        return self._run(
            self._async_client.clone_standup(
                standup_id=standup_id,
                new_name=new_name,
                new_channel=new_channel,
            )
        )

    def pause_standup(self, standup_id: int) -> Standup:
        """Pause a standup by setting wait_time to null."""
        return self._run(self._async_client.pause_standup(standup_id))

    def find_user_by_email(self, email: str) -> Optional[StandupUser]:
        """Find a team member by their email."""
        return self._run(self._async_client.find_user_by_email(email))

    def get_user_standups(self, user_id: int) -> List[Standup]:
        """Get all standups that a user participates in."""
        return self._run(self._async_client.get_user_standups(user_id))

    @staticmethod
    def format_time(hour: int, minute: int = 0) -> str:
        """Format time in HH:MM:SS format."""
        return GeekbotClientAsync.format_time(hour, minute)

    @staticmethod
    def weekday_to_str(day: int) -> str:
        """Convert weekday number (0-6) to three-letter format (Mon-Sun)."""
        return GeekbotClientAsync.weekday_to_str(day)

    def set_log_level(self, level: int) -> None:
        """Set the logging level for this client.

        Parameters
        ----------
        level : int
            The logging level to set (e.g., logging.DEBUG, logging.INFO)
        """
        self.logger.setLevel(level)
        self._async_client.set_log_level(level)
