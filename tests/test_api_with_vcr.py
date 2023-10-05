import pytest
import vcr

from lrclib.api import BASE_URL, ENDPOINTS, LrcLibAPI
from lrclib.exceptions import (
    APIError,
    IncorrectPublishTokenError,
    NotFoundError,
    RateLimitError,
    ServerError,
)


@pytest.fixture(scope="module")
def api() -> LrcLibAPI:
    # Create an instance of the LrcLibAPI class
    _api = LrcLibAPI(user_agent="test_user_agent")
    return _api


my_vcr = vcr.VCR(
    cassette_library_dir="tests/fixtures/cassettes",
    record_mode="once",
)

expected_content = {
    "id": 3396226,
    "name": "I Want to Live",
    "trackName": "I Want to Live",
    "artistName": "Borislav Slavov",
    "albumName": "Baldur's Gate 3 (Original Game Soundtrack)",
    "duration": 233,
    "instrumental": False,
    "lang": "en",
    "isrc": "BGA472329253",
    "spotifyId": "5Y94QNZmNoHid18Y7c5Al9",
    "releaseDate": "2023-08-10T00:00:00Z",
    "plainLyrics": (
        "I feel your breath upon my neck\n...The clock won't stop and this"
        " is what we get\n"
    ),
    "syncedLyrics": (
        "[00:17.12] I feel your breath upon my neck\n...[03:20.31] The"
        " clock won't stop and this is what we get\n[03:25.72] "
    ),
}

expected_search_keys = [
    "id",
    "trackName",
    "artistName",
    "albumName",
    "duration",
    "instrumental",
    "plainLyrics",
    "syncedLyrics",
]


def is_valid_search_result(result: list) -> bool:
    return (
        isinstance(result, list)
        and len(result) > 0
        and all(isinstance(item, dict) for item in result)
        and all(key in result[0] for key in expected_search_keys)
        and all(result[0][key] is not None for key in expected_search_keys)
    )


def is_valid_get_result(result: dict) -> bool:
    return (
        isinstance(result, dict)
        and all(key in result for key in expected_content)
        and all(result[key] is not None for key in expected_content)
    )


@my_vcr.use_cassette()
def test_get_lyrics(api: LrcLibAPI) -> None:
    result = api.get_lyrics(
        "I Want to Live",
        "Borislav Slavov",
        "Baldur's Gate 3 (Original Game Soundtrack)",
        233,
        cached=False,
    )

    assert is_valid_get_result(result)


@my_vcr.use_cassette()
def test_get_lyrics_by_id(api: LrcLibAPI) -> None:
    result = api.get_lyrics_by_id(expected_content["id"])

    assert is_valid_get_result(result)


@my_vcr.use_cassette()
def test_search_with_query(api: LrcLibAPI) -> None:
    result = api.search_lyrics(query="I Want to Live")
    assert is_valid_search_result(result)


@my_vcr.use_cassette()
def test_search_with_fields(api: LrcLibAPI) -> None:
    result = api.search_lyrics(
        track_name="I Want to Live", artist_name="Borislav Slavov"
    )
    assert is_valid_search_result(result)


@my_vcr.use_cassette()
def test_not_found(api: LrcLibAPI) -> None:
    with pytest.raises(NotFoundError):
        api.get_lyrics(
            "this song does not exist",
            "this artist does not exist",
            "this album does not exist",
            233,
            cached=False,
        )