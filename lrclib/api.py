""" API for lrclib"""

import warnings
from typing import Any, Dict, List, Optional

import requests

from .cryptographic_challenge_solver import CryptoChallengeSolver
from .exceptions import (
    APIError,
    IncorrectPublishTokenError,
    NotFoundError,
    RateLimitError,
    ServerError,
)

BASE_URL = "https://lrclib.net/api"
ENDPOINTS: Dict[str, str] = {
    "get": "/get",
    "get_cached": "/get-cached",
    "get_by_id": "/get/{id}",
    "search": "/search",
    "publish": "/publish",
    "request_challenge": "/request-challenge",
}


class LrcLibAPI:
    """API for lrclib"""

    def __init__(
        self,
        user_agent: str,
        base_url: str | None = None,
        session: requests.Session | None = None,
    ):
        self._base_url = base_url or BASE_URL
        self.session = session or requests.Session()

        if not user_agent:
            warnings.warn(
                (
                    "Missing user agent, please set it with the `user_agent`"
                    " argument"
                ),
                UserWarning,
            )
        else:
            self.session.headers.update({"User-Agent": user_agent})

    def _make_request(
        self,
        method: str,
        endpoint: str,
        **kwargs: Any,
    ) -> requests.Response:
        url = self._base_url + endpoint

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            match response.status_code:
                case 404:
                    raise NotFoundError(response) from exc
                case 429:
                    raise RateLimitError(response) from exc
                case _ if 500 <= response.status_code < 600:
                    raise ServerError(response) from exc
                case _:
                    raise APIError(response) from exc

        return response

    def get_lyrics(
        self,
        track_name: str,
        artist_name: str,
        album_name: str,
        duration: int,
        cached: bool = False,
    ) -> Dict[str, Any]:
        endpoint = ENDPOINTS["get_cached" if cached else "get"]
        params = {
            "track_name": track_name,
            "artist_name": artist_name,
            "album_name": album_name,
            "duration": duration,
        }
        response = self._make_request("GET", endpoint, params=params)
        return response.json()

    def get_lyrics_by_id(self, lrclib_id: str | int):
        endpoint = ENDPOINTS["get_by_id"].format(id=lrclib_id)
        response = self._make_request("GET", endpoint)
        return response.json()

    def search_lyrics(
        self,
        query: str | None = None,
        track_name: str | None = None,
        artist_name: str | None = None,
        album_name: str | None = None,
    ) -> List:
        endpoint = ENDPOINTS["search"]
        params = {
            "q": query,
            "track_name": track_name,
            "artist_name": artist_name,
            "album_name": album_name,
        }
        params = {k: v for k, v in params.items() if v is not None}
        try:
            response = self._make_request("GET", endpoint, params=params)
        except NotFoundError:
            return []
        return response.json()

    def request_challenge(self) -> Dict[str, str]:
        """
        Generate a pair of prefix and target strings for the \
            cryptographic challenge. Each challenge has an \
            expiration time of 5 minutes.

        The challenge's solution is a nonce, which can be used \
            to create a Publish Token for submitting lyrics to LRCLIB.

        :return: A dictionary with the following keys: prefix and target.
        """
        endpoint = ENDPOINTS["request_challenge"]
        try:
            response = self._make_request("POST", endpoint)
        except APIError as exc:
            raise APIError(f"Failed to request challenge: {exc}") from exc
        return response.json()

    def obtain_publish_token(self) -> str:
        challenge = self.request_challenge()
        solver = CryptoChallengeSolver()
        nonce = solver.solve_challenge(
            challenge["prefix"], challenge["target"]
        )
        return f"{challenge['prefix']}:{nonce}"

    def publish_lyrics(
        self,
        track_name: str,
        artist_name: str,
        album_name: str,
        duration: int,
        plain_lyrics: Optional[str] = None,
        synced_lyrics: Optional[str] = None,
        publish_token: Optional[str] = None,
    ) -> requests.Response:
        endpoint = ENDPOINTS["publish"]

        if not publish_token:
            publish_token = self.obtain_publish_token()

        headers = {"X-Publish-Token": publish_token}
        data = {
            "trackName": track_name,
            "artistName": artist_name,
            "albumName": album_name,
            "duration": duration,
            "plainLyrics": plain_lyrics,
            "syncedLyrics": synced_lyrics,
        }

        try:
            response = self._make_request(
                "POST", endpoint, headers=headers, json=data
            )
            return response.json()

        except APIError as exc:
            if exc.status_code == 400:
                raise IncorrectPublishTokenError(
                    "Incorrect publish token"
                ) from exc
            raise APIError(f"Failed to publish lyrics: {exc}") from exc
