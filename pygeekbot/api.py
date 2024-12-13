"""Direct implementation of the Geekbot API endpoints."""

from typing import List, Optional, Dict, Any
import httpx
import logging
import msgspec
from .models import (
    Standup,
    StandupReport,
    StandupCreate,
    StandupUpdate,
    ReportCreate,
    Team,
)
from .exceptions import (
    GeekbotAPIError,
    GeekbotNotFoundError,
    GeekbotAuthError,
    GeekbotValidationError,
    GeekbotRateLimitError,
    GeekbotServerError,
)
from datetime import datetime, timedelta
import backoff
from collections import deque
from typing import Deque
import asyncio


class GeekbotApiClient:
    """Async client for the Geekbot API."""

    BASE_URL = "https://api.geekbot.com/v1"

    def __init__(self, api_key: str, rate_limit: int = 60):
        """Initialize the client with an API key."""
        self.api_key = api_key
        auth_header = api_key if api_key.startswith("api_") else f"Bearer {api_key}"
        self.headers = {
            "Authorization": auth_header,
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers=self.headers,
        )
        self.logger = logging.getLogger("geekbot.api")
        self._rate_limit = rate_limit  # requests per minute
        self._request_times: Deque[datetime] = deque(maxlen=rate_limit)
        self._rate_limit_lock = asyncio.Lock()

    def _handle_errors(self, response: httpx.Response) -> None:
        """Handle common API errors."""
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise GeekbotAuthError(e.response.status_code, str(e))
            elif e.response.status_code == 404:
                raise GeekbotNotFoundError(e.response.status_code, str(e))
            elif e.response.status_code == 422:
                raise GeekbotValidationError(e.response.status_code, str(e))
            elif e.response.status_code == 429:
                raise GeekbotRateLimitError(e.response.status_code, str(e))
            elif e.response.status_code >= 500:
                raise GeekbotServerError(e.response.status_code, str(e))
            else:
                raise GeekbotAPIError(e.response.status_code, str(e))

    def _encode_json(self, data: Any) -> bytes:
        """Encode data to JSON bytes."""
        return msgspec.json.encode(data)

    def _decode_json(self, content: bytes, type: type) -> Any:
        """Decode JSON bytes to specified type."""
        return msgspec.json.decode(content, type=type)

    async def get_standups(self) -> List[Standup]:
        """Get all standups."""
        try:
            response = await self._make_request("GET", "/standups")
            return self._decode_json(response.content, type=List[Standup])
        except Exception as e:
            self.logger.error(f"Unexpected error fetching standups: {e}")
            raise

    async def get_standup(self, standup_id: int) -> Standup:
        """Get a specific standup by ID."""
        try:
            response = await self._make_request("GET", f"/standups/{standup_id}")
            return self._decode_json(response.content, type=Standup)
        except Exception as e:
            self.logger.error(f"Unexpected error fetching standup {standup_id}: {e}")
            raise

    async def create_standup(self, standup: StandupCreate) -> Standup:
        """Creates a new standup."""
        self.logger.debug(f"Creating new standup with name: {standup.name}")
        try:
            response = await self._make_request(
                "POST",
                "/standups",
                content=self._encode_json(standup),
            )
            return self._decode_json(response.content, type=Standup)
        except Exception as e:
            self.logger.error(f"Unexpected error creating standup: {e}")
            raise

    async def update_standup(self, standup_id: int, update: StandupUpdate) -> Standup:
        """Update an existing standup.

        Parameters
        ----------
        standup_id : int
            ID of the standup to update
        update : StandupUpdate
            The update configuration

        Returns
        -------
        Standup
            The updated standup details
        """
        try:
            response = await self._make_request(
                "PATCH",
                f"/standups/{standup_id}",
                content=self._encode_json(update),
            )
            return self._decode_json(response.content, type=Standup)
        except Exception as e:
            self.logger.error(f"Unexpected error updating standup {standup_id}: {e}")
            raise

    async def delete_standup(self, standup_id: int) -> None:
        """Delete a standup."""
        try:
            await self._make_request("DELETE", f"/standups/{standup_id}")
        except Exception as e:
            self.logger.error(f"Unexpected error deleting standup {standup_id}: {e}")
            raise

    async def get_reports(
        self,
        standup_id: Optional[int] = None,
        limit: Optional[int] = None,
        user_id: Optional[int] = None,
        after: Optional[int] = None,
        before: Optional[int] = None,
        question_ids: Optional[List[int]] = None,
        html: Optional[bool] = None,
    ) -> List[StandupReport]:
        """Get standup reports with optional filters."""
        params = {}
        if standup_id is not None:
            params["standup_id"] = standup_id
        if limit is not None:
            params["limit"] = limit
        if user_id is not None:
            params["user_id"] = user_id
        if after is not None:
            params["after"] = after
        if before is not None:
            params["before"] = before
        if question_ids is not None:
            params["question_ids"] = question_ids
        if html is not None:
            params["html"] = html

        try:
            response = await self._make_request("GET", "/reports", params=params)
            return self._decode_json(response.content, type=List[StandupReport])
        except Exception as e:
            self.logger.error(f"Unexpected error fetching reports: {e}")
            raise

    async def get_report(self, report_id: int) -> StandupReport:
        """Get a specific report by ID."""
        try:
            response = await self._make_request("GET", f"/reports/{report_id}")
            return self._decode_json(response.content, type=StandupReport)
        except Exception as e:
            self.logger.error(f"Unexpected error fetching report {report_id}: {e}")
            raise

    async def create_report(self, report: ReportCreate) -> StandupReport:
        """Create a new report.

        Parameters
        ----------
        report : ReportCreate
            The report configuration to create

        Returns
        -------
        StandupReport
            The created report details
        """
        try:
            response = await self._make_request(
                "POST",
                "/reports",
                content=self._encode_json(report),
            )
            return self._decode_json(response.content, type=StandupReport)
        except Exception as e:
            self.logger.error(f"Unexpected error creating report: {e}")
            raise

    async def get_team(self) -> Team:
        """Get team information."""
        try:
            response = await self._make_request("GET", "/teams")
            return self._decode_json(response.content, type=Team)
        except Exception as e:
            self.logger.error(f"Unexpected error fetching team information: {e}")
            raise

    async def duplicate_standup(
        self,
        standup_id: int,
        name: str,
        channel: Optional[str] = None,
        time: Optional[str] = None,
        timezone: Optional[str] = None,
        wait_time: Optional[int] = None,
        days: Optional[List[str]] = None,
        questions: Optional[List[Dict[str, str]]] = None,
        users: Optional[List[int]] = None,
        sync_channel_members: Optional[bool] = None,
        personalised: Optional[bool] = None,
    ) -> Standup:
        """Duplicate an existing standup with optional modifications."""
        data = {
            "name": name,  # Required parameter
        }
        # Add optional parameters only if they are provided
        if channel is not None:
            data["channel"] = channel
        if time is not None:
            data["time"] = time
        if timezone is not None:
            data["timezone"] = timezone
        if wait_time is not None:
            data["wait_time"] = wait_time
        if days is not None:
            data["days"] = days
        if questions is not None:
            data["questions"] = questions
        if users is not None:
            data["users"] = users
        if sync_channel_members is not None:
            data["sync_channel_members"] = sync_channel_members
        if personalised is not None:
            data["personalised"] = personalised

        try:
            response = await self._make_request(
                "POST",
                f"/standups/{standup_id}/duplicate",
                content=self._encode_json(data),
            )
            return self._decode_json(response.content, type=Standup)
        except Exception as e:
            self.logger.error(f"Unexpected error duplicating standup {standup_id}: {e}")
            raise

    async def start_standup(
        self,
        standup_id: int,
        user_ids: Optional[List[int]] = None,
        emails: Optional[List[str]] = None,
    ) -> str:
        """Start a standup for specific users.

        Returns
        -------
        str
            Response message from the API, usually "ok"
        """
        data = {}
        if user_ids:
            data["user_ids"] = user_ids
        if emails:
            data["emails"] = emails

        try:
            response = await self._make_request(
                "POST",
                f"/standups/{standup_id}/start",
                content=self._encode_json(data),
            )
            # The API returns a simple string, not a JSON object
            return response.content.decode("utf-8").strip('"')
        except Exception as e:
            self.logger.error(f"Unexpected error starting standup {standup_id}: {e}")
            raise

    async def replace_standup(self, standup_id: int, standup: StandupCreate) -> Standup:
        """Replace an existing standup.

        Parameters
        ----------
        standup_id : int
            ID of the standup to replace
        standup : StandupCreate
            The new standup configuration

        Returns
        -------
        Standup
            The replaced standup details
        """
        try:
            response = await self._make_request(
                "PUT",
                f"/standups/{standup_id}",
                content=self._encode_json(standup),
            )
            return self._decode_json(response.content, type=Standup)
        except Exception as e:
            self.logger.error(f"Unexpected error replacing standup {standup_id}: {e}")
            raise

    def set_log_level(self, level: int) -> None:
        """Set the logging level for the client."""
        self.logger.setLevel(level)

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()

    async def __aenter__(self) -> "GeekbotApiClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()

    async def _wait_for_rate_limit(self):
        """Wait if necessary to respect rate limits.

        Uses a token bucket style rate limiter with a sliding window.
        """
        async with self._rate_limit_lock:
            now = datetime.now()
            window_start = now - timedelta(minutes=1)

            # Remove requests older than 1 minute
            while self._request_times and self._request_times[0] < window_start:
                self._request_times.popleft()

            if len(self._request_times) >= self._rate_limit:
                # Calculate wait time based on oldest request
                wait_time = 60 - (now - self._request_times[0]).total_seconds()
                if wait_time > 0:
                    self.logger.debug(
                        f"Rate limit reached, waiting {wait_time:.2f} seconds"
                    )
                    await asyncio.sleep(wait_time)

            # Add current request time
            self._request_times.append(now)

    @backoff.on_exception(
        backoff.expo,
        (GeekbotServerError, httpx.TransportError, GeekbotRateLimitError),
        max_tries=3,
        giveup=lambda e: isinstance(e, GeekbotAuthError),
    )
    async def _make_request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make an HTTP request with retry logic and rate limiting.

        Parameters
        ----------
        method : str
            HTTP method (GET, POST, etc.)
        url : str
            API endpoint URL
        **kwargs : dict
            Additional arguments to pass to httpx.request

        Returns
        -------
        httpx.Response
            The API response

        Raises
        ------
        GeekbotAPIError
            If the request fails after retries
        """
        await self._wait_for_rate_limit()

        try:
            response = await self.client.request(method, url, **kwargs)
            self._handle_errors(response)
            return response
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:  # Rate limit error
                self.logger.warning("Rate limit exceeded, backing off...")
                raise GeekbotRateLimitError(e.response.status_code, str(e))
            raise
