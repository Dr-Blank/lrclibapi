from datetime import datetime
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

from lrclib.models import (
    CryptographicChallenge,
    Lyrics,
    LyricsMinimal,
    SearchResult,
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
        "I feel your breath upon my neck\nA soft caress as cold as death\n"
    ),
    "syncedLyrics": (
        "[00:17.12] I feel your breath upon my neck\n[00:20.41] A soft caress"
        " as cold as death\n"
    ),
}


def is_valid_search_result(result: SearchResult) -> bool:
    return (
        isinstance(result, SearchResult)
        and len(result) > 0
        and all(isinstance(item, LyricsMinimal) for item in result)
    )


def is_valid_get_result(result: Lyrics) -> bool:
    return (
        isinstance(result, Lyrics)
        and result.name == expected_content["name"]
        and result.track_name == expected_content["trackName"]
        and result.artist_name == expected_content["artistName"]
        and result.album_name == expected_content["albumName"]
        and result.duration == expected_content["duration"]
        and result.instrumental == expected_content["instrumental"]
        and result.plain_lyrics.startswith(expected_content["plainLyrics"])
        and result.synced_lyrics.startswith(expected_content["syncedLyrics"])
        and result.lang == expected_content["lang"]
        and result.isrc == expected_content["isrc"]
        and result.spotify_id == expected_content["spotifyId"]
        and result.release_date == datetime(2023, 8, 10, 0, 0, 0)
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


# test request challenge
@my_vcr.use_cassette()
def test_request_challenge(api: LrcLibAPI) -> None:
    result = api.request_challenge()
    assert isinstance(result, CryptographicChallenge)
