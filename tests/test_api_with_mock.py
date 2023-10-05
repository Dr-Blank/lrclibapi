from unittest.mock import Mock

import pytest

from lrclib.api import BASE_URL, ENDPOINTS, LrcLibAPI
from lrclib.exceptions import (
    APIError,
    NotFoundError,
    RateLimitError,
    ServerError,
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

    # Check that the result is the expected dictionary
    assert result == sample_response


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

    # Check that the result is the expected dictionary
    assert result == {"lyrics": "test lyrics"}


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

    # Check that the result is the expected dictionary
    assert result == {"lyrics": "test lyrics"}


def test_search_lyrics(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    session_mock.request.return_value.json.return_value = [
        {"lyrics": "test lyrics"}
    ]

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the search_lyrics method
    result = api.search_lyrics(query="test_query")

    # Check that the session's request method was called with the correct arguments
    session_mock.request.assert_called_once_with(
        "GET", BASE_URL + ENDPOINTS["search"], params={"q": "test_query"}
    )

    # Check that the result is the expected list
    assert result == [{"lyrics": "test lyrics"}]


def test_request_challenge(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    session_mock.request.return_value.json.return_value = {
        "prefix": "test_prefix",
        "target": "test_target",
    }

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the request_challenge method
    result = api.request_challenge()

    # Check that the session's request method was called with the correct arguments
    session_mock.request.assert_called_once_with(
        "POST", BASE_URL + ENDPOINTS["request_challenge"]
    )

    # Check that the result is the expected dictionary
    assert result == {"prefix": "test_prefix", "target": "test_target"}


def test_publish_lyrics(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    session_mock.request.return_value.json.return_value = {"status": "success"}

    # Mock the obtain_publish_token method of the LrcLibAPI instance
    api_mock = Mock()
    api_mock.obtain_publish_token.return_value = "test_publish_token"

    # Set the session object and obtain_publish_token method of the LrcLibAPI instance to the mock objects
    api.session = session_mock
    api.obtain_publish_token = api_mock.obtain_publish_token

    # Call the publish_lyrics method
    result = api.publish_lyrics(
        "test_track_name",
        "test_artist_name",
        "test_album_name",
        180,
        plain_lyrics="test_plain_lyrics",
        synced_lyrics="test_synced_lyrics",
    )

    # Check that the obtain_publish_token method was called
    api_mock.obtain_publish_token.assert_called_once()

    # Check that the session's request method was called with the correct arguments
    session_mock.request.assert_called_once_with(
        "POST",
        BASE_URL + ENDPOINTS["publish"],
        headers={"X-Publish-Token": "test_publish_token"},
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
    session_mock.request.side_effect = RateLimitError(Mock(status_code=429))

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the search_lyrics method and check that it raises a RateLimitError
    with pytest.raises(RateLimitError):
        api.search_lyrics(query="test_query")


def test_server_error(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    session_mock.request.side_effect = ServerError(Mock(status_code=500))

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the get_lyrics_by_id method and check that it raises a ServerError
    with pytest.raises(ServerError):
        api.get_lyrics_by_id(123)


# def test_incorrect_publish_token_error(api: LrcLibAPI) -> None:
#     # Mock the requests.Session object
#     session_mock = Mock()
#     session_mock.request.side_effect = APIError(Mock(status_code=400))

#     # Set the session object of the LrcLibAPI instance to the mock object
#     api.session = session_mock

#     # Call the publish_lyrics method and check that it raises an IncorrectPublishTokenError
#     with pytest.raises(IncorrectPublishTokenError):
#         api.publish_lyrics(
#             "test_track_name",
#             "test_artist_name",
#             "test_album_name",
#             180,
#             plain_lyrics="test_plain_lyrics",
#             synced_lyrics="test_synced_lyrics",
#             publish_token="incorrect_publish_token"
#         )


def test_api_error(api: LrcLibAPI) -> None:
    # Mock the requests.Session object
    session_mock = Mock()
    session_mock.request.side_effect = APIError(Mock(status_code=401))

    # Set the session object of the LrcLibAPI instance to the mock object
    api.session = session_mock

    # Call the request_challenge method and check that it raises an APIError
    with pytest.raises(APIError):
        api.get_lyrics_by_id(123)
