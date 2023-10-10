from unittest.mock import Mock
import warnings

import pytest
from requests import HTTPError, Response

from lrclib.api import BASE_URL, ENDPOINTS, LrcLibAPI
from lrclib.exceptions import (
    APIError,
    IncorrectPublishTokenError,
    NotFoundError,
    RateLimitError,
    ServerError,
)
from lrclib.models import (
    Lyrics,
    LyricsMinimal,
    SearchResult,
    CryptographicChallenge,
)


@pytest.fixture(scope="module")
def api() -> LrcLibAPI:
    # Create an instance of the LrcLibAPI class
    _api = LrcLibAPI(user_agent="test_user_agent")
    # mock = Mock()
    # api.session = mock
    return _api


def test_not_found_error(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    session_mock.request.side_effect = NotFoundError(Mock(status_code=404))

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the get_lyrics method and check that it raises a NotFoundError
    with pytest.raises(NotFoundError):
        api.get_lyrics(
            "test_track_name", "test_artist_name", "test_album_name", 180
        )


def test_rate_limit_error(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    mock_error = HTTPError(response=Response())
    mock_error.response.status_code = 429
    session_mock.request.side_effect = mock_error

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the search_lyrics method and check that it raises a RateLimitError
    with pytest.raises(RateLimitError):
        api.search_lyrics(query="test_query")


def test_server_error(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    mock_error = HTTPError(response=Response())
    mock_error.response.status_code = 500
    session_mock.request.side_effect = mock_error

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the get_lyrics_by_id method and check that it raises a ServerError
    with pytest.raises(ServerError):
        api.get_lyrics_by_id(123)


def test_incorrect_publish_token_error(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    mock_error = HTTPError(response=Response())
    mock_error.response.status_code = 400
    session_mock.request.side_effect = mock_error
    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    with pytest.raises(IncorrectPublishTokenError):
        api.publish_lyrics(
            "test_track_name",
            "test_artist_name",
            "test_album_name",
            180,
            plain_lyrics="test_plain_lyrics",
            synced_lyrics="test_synced_lyrics",
            publish_token="incorrect_publish_token",
        )


def test_api_error(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    mock_error = HTTPError(response=Response())
    mock_error.response.status_code = 403
    session_mock.request.side_effect = mock_error

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the request_challenge method and check that it raises an APIError
    with pytest.raises(APIError):
        api.get_lyrics_by_id(123)


# test if warning is raised when user agent is not set
def test_no_user_agent_warning() -> None:
    with pytest.warns(UserWarning, match="user_agent") as record:
        LrcLibAPI(user_agent="")
    assert len(record) == 1


# test if warning is not raised when user agent is set
def test_user_agent_no_warning() -> None:
    with warnings.catch_warnings(record=True) as record:
        LrcLibAPI(user_agent="test_user_agent")
    assert len(record) == 0


# test raise ValueError when search_lyrics is called without query or track_name
def test_invalid_search_lyrics(api: LrcLibAPI) -> None:
    with pytest.raises(ValueError):
        api.search_lyrics(artist_name="test_artist_name")

    with pytest.raises(ValueError):
        api.search_lyrics(album_name="test_album_name")


# check if search result is empty when 404 is returned
def test_search_lyrics_empty(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    mock_error = HTTPError(response=Response())
    mock_error.response.status_code = 404
    session_mock.request.side_effect = mock_error

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the search_lyrics method and check that it returns an empty list
    assert api.search_lyrics(query="test_query") == SearchResult([])


# check if error is raised when request_challenge is called and 500 is returned
def test_request_challenge_500(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    mock_error = HTTPError(response=Response())
    mock_error.response.status_code = 500
    session_mock.request.side_effect = mock_error

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the request_challenge method and check that it raises a ServerError
    with pytest.raises(ServerError):
        api.request_challenge()