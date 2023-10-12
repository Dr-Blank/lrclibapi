""" API for lrclib"""

import os
import warnings
from typing import Any, Dict, Optional

import requests

from .cryptographic_challenge_solver import CryptoChallengeSolver
from .exceptions import (
    APIError,
    IncorrectPublishTokenError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from .models import CryptographicChallenge, Lyrics, SearchResult

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
                "Missing user agent"
                + "please set it with the `user_agent` argument",
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
            response = exc.response
            match response.status_code:
                case 404:
                    raise NotFoundError(response) from exc
                case 429:
                    raise RateLimitError(response) from exc
                case 400:
                    raise IncorrectPublishTokenError(response) from exc
                case _ if 500 <= response.status_code < 600:
                    raise ServerError(response) from exc
                case _:
                    raise APIError(response) from exc

        return response

    def get_lyrics(  # pylint: disable=too-many-arguments
        self,
        track_name: str,
        artist_name: str,
        album_name: str,
        duration: int,
        cached: bool = False,
    ) -> Lyrics:
        """
        Get lyrics from LRCLIB.

        :param track_name: name of the track
        :type track_name: str
        :param artist_name: name of the artist
        :type artist_name: str
        :param album_name: name of the album
        :type album_name: str
        :param duration: duration of the track in seconds
        :type duration: int
        :param cached: set to True to get cached lyrics, defaults to False
        :type cached: bool, optional
        :return: a dictionary with response data
        :rtype: Lyrics
        """

        endpoint = ENDPOINTS["get_cached" if cached else "get"]
        params = {
            "track_name": track_name,
            "artist_name": artist_name,
            "album_name": album_name,
            "duration": duration,
        }
        response = self._make_request("GET", endpoint, params=params)
        return Lyrics.from_dict(response.json())

    def get_lyrics_by_id(self, lrclib_id: str | int) -> Lyrics:
        """
        Get lyrics from LRCLIB by ID.

        :param lrclib_id: ID of the lyrics
        :type lrclib_id: str | int
        :return: a dictionary with response data
        :rtype: :class:`Lyrics`
        """
        endpoint = ENDPOINTS["get_by_id"].format(id=lrclib_id)
        response = self._make_request("GET", endpoint)
        return Lyrics.from_dict(response.json())

    def search_lyrics(
        self,
        query: str | None = None,
        track_name: str | None = None,
        artist_name: str | None = None,
        album_name: str | None = None,
    ) -> SearchResult:
        """
        Search lyrics from LRCLIB.

        :param query: query string, defaults to None
        :type query: str | None, optional
        :param track_name: defaults to None
        :type track_name: str | None, optional
        :param artist_name: defaults to None
        :type artist_name: str | None, optional
        :param album_name: defaults to None
        :type album_name: str | None, optional
        :return: a list of search results
        :rtype: :class:`SearchResult`
        """
        # either query or track_name is required
        if not query and not track_name:
            raise ValueError(
                "Either query or track_name is required to search lyrics"
            )

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
            return SearchResult([])
        return SearchResult.from_list(response.json())

    def request_challenge(self) -> CryptographicChallenge:
        """
        Generate a pair of prefix and target strings for the \
            cryptographic challenge. Each challenge has an \
            expiration time of 5 minutes.

        The challenge's solution is a nonce, which can be used \
            to create a Publish Token for submitting lyrics to LRCLIB.

        :return: :class:`CryptographicChallenge`
        """
        endpoint = ENDPOINTS["request_challenge"]
        try:
            response = self._make_request("POST", endpoint)
        except APIError as exc:
            raise exc
        return CryptographicChallenge.from_dict(response.json())

    def _obtain_publish_token(self) -> str:
        """
        Obtain a Publish Token for submitting lyrics to LRCLIB.

        :return: A Publish Token
        :rtype: str
        """

        num_threads = os.cpu_count() or 1
        challenge = self.request_challenge()
        nonce = CryptoChallengeSolver.solve(
            challenge.prefix, challenge.target, num_threads=num_threads
        )
        return f"{challenge.prefix}:{nonce}"

    def publish_lyrics(  # pylint: disable=too-many-arguments
        self,
        track_name: str,
        artist_name: str,
        album_name: str,
        duration: int,
        plain_lyrics: Optional[str] = None,
        synced_lyrics: Optional[str] = None,
        publish_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Publish lyrics to LRCLIB.

        :param track_name:
        :type track_name: str
        :param artist_name:
        :type artist_name: str
        :param album_name:
        :type album_name: str
        :param duration:
        :type duration: int
        :param plain_lyrics: , defaults to None
        :type plain_lyrics: Optional[str], optional
        :param synced_lyrics: , defaults to None
        :type synced_lyrics: Optional[str], optional
        :param publish_token: token for publishing lyrics, to obtain a new \
            token, use the `obtain_publish_token` method, defaults to None
        :type publish_token: Optional[str], optional
        :raises IncorrectPublishTokenError: if the publish token is incorrect
        :raises APIError: if the request fails
        :return: a dictionary with response data
        :rtype: Dict[str, Any]
        """
        endpoint = ENDPOINTS["publish"]

        if not publish_token:
            publish_token = self._obtain_publish_token()

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
            raise exc
