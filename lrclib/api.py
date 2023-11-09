""" API for lrclib"""

import os
import warnings
from http import HTTPStatus
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
    """
    Create a new LrcLibAPI instance. You can optionally pass a custom \
        base URL and a custom requests session.

    .. note::
        setting `user_agent` is not required, but it is recommended by LRCLIB.

    Parameters
    ----------
    user_agent : str
        User agent to use for the requests
    base_url : str, optional
        Base URL to use for the requests
    session : requests.Session, optional
        Requests session to use for the requests

    Raises
    ------
    UserWarning
        If user_agent is not set

    Examples
    --------
    See the :doc:`examples/fetch_lyrics` section for usage examples.
    """

    def __init__(
        self,
        user_agent: str,
        base_url: "str | None" = None,
        session: "requests.Session | None" = None,
    ):
        self._base_url = base_url or BASE_URL
        self.session = session or requests.Session()

        if not user_agent:
            warnings.warn(
                "Missing user agent, please set it with the `user_agent`"
                " argument",
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
            response = exc.response  # type: ignore
            if response.status_code == HTTPStatus.NOT_FOUND:
                raise NotFoundError(response) from exc
            if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                raise RateLimitError(response) from exc
            if response.status_code == HTTPStatus.BAD_REQUEST:
                raise IncorrectPublishTokenError(response) from exc
            if 500 <= response.status_code < 600:
                raise ServerError(response) from exc
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
        Get lyrics from LRCLIB by track name, artist name, album name and \
            duration.

        .. note::
            All parameters are required except `cached`.

        Parameters
        ----------
        track_name : str
            Track name
        artist_name : str
            Artist name
        album_name : str
            Album name
        duration : int
            Duration of the track in seconds
        cached : bool, optional
            Whether to get cached lyrics or not, defaults to False

        Returns
        -------
        Lyrics

        Raises
        ------
        NotFoundError
            If no lyrics are found
        APIError
            If the request fails
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

    def get_lyrics_by_id(self, lrclib_id: "str | int") -> Lyrics:
        """
        Get lyrics from LRCLIB by ID.

        Parameters
        ----------
        lrclib_id : str | int
            ID of the lyrics

        Returns
        -------
        Lyrics

        Raises
        ------
        NotFoundError
            If no lyrics are found
        APIError
            If the request fails
        """
        endpoint = ENDPOINTS["get_by_id"].format(id=lrclib_id)
        response = self._make_request("GET", endpoint)
        return Lyrics.from_dict(response.json())

    def search_lyrics(
        self,
        query: "str | None" = None,
        track_name: "str | None" = None,
        artist_name: "str | None" = None,
        album_name: "str | None" = None,
    ) -> SearchResult:
        """
        Search lyrics on LRCLIB by query, track name, artist name and/or \
            album name.

        .. note::
            Either `query` or `track_name` is required.

        Parameters
        ----------
        query : str, optional
            Search query
        track_name : str, optional
            Track name
        artist_name : str, optional
            Artist name
        album_name : str, optional
            Album name

        Returns
        -------
        SearchResult

        Raises
        ------
        APIError
            If the request fails
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

        Returns
        -------
        CryptographicChallenge

        See Also
        --------
        publish_lyrics : Submit lyrics to LRCLIB directly without \
            using the `request_challenge` method

        :obj:`~lrclib.cryptographic_challenge_solver` : Use one of the \
            available solvers to solve the challenge

        Raises
        ------
        APIError
            If the request fails
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

        Returns
        -------
        publish_token : str
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
        Publish lyrics to LRCLIB. All parameters are required.

        .. note::
            If no lyrics are provided, the track will be marked as \
                instrumental.

        Parameters
        ----------
        track_name : str
            Track name
        artist_name : str
            Artist name
        album_name : str
            Album name
        duration : int
            Duration of the track in seconds
        plain_lyrics : str, optional
            Plain lyrics
        synced_lyrics : str, optional
            Synced lyrics
        publish_token : str, optional
            Publish token to use for publishing lyrics, if not provided, \
                a new one will be generated

        Returns
        -------
        Dict[str, Any]
            Response from the API

        Raises
        ------
        IncorrectPublishTokenError
            If the publish token is incorrect
        APIError
            If the request fails
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
