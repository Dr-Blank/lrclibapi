import os
import warnings
from unittest.mock import Mock

import pytest
from requests import HTTPError, Response

from lrclibapi.api import BASE_URL, ENDPOINTS, LrcLibAPI
from lrclibapi.cryptographic_challenge_solver import CryptoChallengeSolver
from lrclibapi.exceptions import (
    APIError,
    IncorrectPublishTokenError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from lrclibapi.models import (
    CryptographicChallenge,
    Lyrics,
    LyricsMinimal,
    SearchResult,
)


@pytest.fixture(scope="module")
def api() -> LrcLibAPI:
    # Create an instance of the LrcLibAPI class
    _api = LrcLibAPI(user_agent="test_user_agent")
    # mock = Mock()
    # api.session = mock
    return _api


def test_get_lyrics(
    api: LrcLibAPI,  # pylint: disable=redefined-outer-name
) -> None:
    # Set up a sample track signature
    track_name = "I Want to Live"
    artist_name = "Borislav Slavov"
    album_name = "Baldur's Gate 3 (Original Game Soundtrack)"
    duration = 233

    # Set up a sample response
    sample_response = {
        "id": 3396226,
        "trackName": track_name,
        "artistName": artist_name,
        "albumName": album_name,
        "duration": duration,
        "instrumental": False,
        "plainLyrics": (
            "I feel your breath upon my neck\n...The clock won't stop and this"
            " is what we get\n"
        ),
        "syncedLyrics": (
            "[00:17.12] I feel your breath upon my neck\n...[03:20.31] The"
            " clock won't stop and this is what we get\n[03:25.72] "
        ),
    }
    # Mock the requests.Session object
    session_mock = Mock()
    session_mock.request.return_value.json.return_value = sample_response

    api.session = session_mock

    result = api.get_lyrics(
        track_name, artist_name, album_name, duration, cached=False
    )

    session_mock.request.assert_called_once_with(
        "GET",
        BASE_URL + ENDPOINTS["get"],
        params={
            "track_name": track_name,
            "artist_name": artist_name,
            "album_name": album_name,
            "duration": duration,
        },
    )

    # Check that the result is the expected
    assert result == Lyrics.from_dict(sample_response)


def test_get_cached_lyrics(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    session_mock.request.return_value.json.return_value = {
        "lyrics": "test lyrics"
    }

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the get_lyrics method with the cached argument set to True
    result = api.get_lyrics(
        "test_track_name",
        "test_artist_name",
        "test_album_name",
        180,
        cached=True,
    )

    # Check that the session's request method was called with the correct arguments
    session_mock.request.assert_called_once_with(
        "GET",
        BASE_URL + ENDPOINTS["get_cached"],
        params={
            "track_name": "test_track_name",
            "artist_name": "test_artist_name",
            "album_name": "test_album_name",
            "duration": 180,
        },
    )

    assert result == Lyrics.from_dict({"lyrics": "test lyrics"})


def test_get_lyrics_by_id(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    session_mock.request.return_value.json.return_value = {
        "lyrics": "test lyrics"
    }

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the get_lyrics_by_id method
    result = api.get_lyrics_by_id(123)

    # Check that the session's request method was called with the correct arguments
    session_mock.request.assert_called_once_with(
        "GET", BASE_URL + ENDPOINTS["get_by_id"].format(id=123)
    )

    assert result == Lyrics.from_dict({"lyrics": "test lyrics"})


def test_search_lyrics(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    test_lyrics = {"lyrics": "test lyrics"}
    session_mock.request.return_value.json.return_value = [test_lyrics]

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the search_lyrics method
    result = api.search_lyrics(query="test_query")

    # Check that the session's request method was called with the correct arguments
    session_mock.request.assert_called_once_with(
        "GET", BASE_URL + ENDPOINTS["search"], params={"q": "test_query"}
    )

    assert result == SearchResult([LyricsMinimal.from_dict(test_lyrics)])


def test_request_challenge(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    sample_return = {
        "prefix": "test_prefix",
        "target": "test_target",
    }

    session_mock.request.return_value.json.return_value = sample_return

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the request_challenge method
    result = api.request_challenge()

    # Check that the session's request method was called with the correct arguments
    session_mock.request.assert_called_once_with(
        "POST", BASE_URL + ENDPOINTS["request_challenge"]
    )

    assert result == CryptographicChallenge.from_dict(sample_return)


def test_publish_lyrics(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    session_mock.request.return_value.json.return_value = {"status": "success"}

    # Mock the challenge
    request_challenge = Mock()
    simple_challenge = CryptographicChallenge("test_prefix", "0f")
    solution = CryptoChallengeSolver.solve(
        simple_challenge.prefix,
        simple_challenge.target,
        num_threads=os.cpu_count() or 1,
    )
    request_challenge.return_value = simple_challenge

    api.session = session_mock
    api.request_challenge = request_challenge

    # Call the publish_lyrics method
    result = api.publish_lyrics(
        "test_track_name",
        "test_artist_name",
        "test_album_name",
        180,
        plain_lyrics="test_plain_lyrics",
        synced_lyrics="test_synced_lyrics",
    )

    # Check that the session's request method was called with the correct arguments
    session_mock.request.assert_called_once_with(
        "POST",
        BASE_URL + ENDPOINTS["publish"],
        headers={"X-Publish-Token": f"{simple_challenge.prefix}:{solution}"},
        json={
            "trackName": "test_track_name",
            "artistName": "test_artist_name",
            "albumName": "test_album_name",
            "duration": 180,
            "plainLyrics": "test_plain_lyrics",
            "syncedLyrics": "test_synced_lyrics",
        },
    )

    # Check that the result is the expected dictionary
    assert result == {"status": "success"}
