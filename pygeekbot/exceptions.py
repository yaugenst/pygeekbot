class GeekbotError(Exception):
    """Base exception for Geekbot errors."""

    pass


class GeekbotAPIError(GeekbotError):
    """Raised when the API returns an error."""

    def __init__(self, status_code: int, message: str):
        self.status_code = status_code
        self.message = message
        super().__init__(f"API Error {status_code}: {message}")


class GeekbotAuthError(GeekbotAPIError):
    """Raised when authentication fails."""

    pass


class GeekbotNotFoundError(GeekbotAPIError):
    """Raised when a resource is not found."""

    pass


class GeekbotValidationError(GeekbotAPIError):
    """Raised when request validation fails."""

    pass


class GeekbotRateLimitError(GeekbotAPIError):
    """Raised when API rate limit is exceeded."""

    pass


class GeekbotServerError(GeekbotAPIError):
    """Raised when server returns 5xx error."""

    pass
