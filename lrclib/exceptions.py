"""Exceptions for the LRC API."""

import requests


class APIError(requests.exceptions.RequestException):
    """Base class for API errors."""

    def __init__(self, response: requests.Response) -> None:
        self.response = response
        self.status_code = response.status_code
        self.reason = response.reason
        self.url = response.url
        self.text = response.text
        self.headers = response.headers

        super().__init__(f"{self.status_code} {self.reason} for {self.url}")


class NotFoundError(APIError):
    """Raised when a resource is not found."""


class ServerError(APIError):
    """Raised when the server returns an error."""


class RateLimitError(APIError):
    """Raised when the rate limit is exceeded."""


class IncorrectPublishTokenError(APIError):
    """Raised when the publish token is incorrect."""
