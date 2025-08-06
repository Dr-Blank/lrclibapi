from datetime import datetime
import pytest
import vcr

from lrclibapi.api import BASE_URL, ENDPOINTS, LrcLibAPI
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
    return _api


my_vcr = vcr.VCR(
    cassette_library_dir="tests/fixtures/cassettes",
    decode_compressed_response=True,
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


def validate_get_result(result: Lyrics) -> None:
    """Validate the get result with individual assertions for better error messages."""
    assert isinstance(result, Lyrics), "Result should be an instance of Lyrics"
    assert result.name == expected_content["name"], (
        f"Name mismatch. Expected: {expected_content['name']}, Got: {result.name}"
    )
    assert result.track_name == expected_content["trackName"], (
        f"Track name mismatch. Expected: {expected_content['trackName']}, Got: {result.track_name}"
    )
    assert result.artist_name == expected_content["artistName"], (
        f"Artist name mismatch. Expected: {expected_content['artistName']}, Got: {result.artist_name}"
    )
    assert result.album_name == expected_content["albumName"], (
        f"Album name mismatch. Expected: {expected_content['albumName']}, Got: {result.album_name}"
    )
    assert result.duration == expected_content["duration"], (
        f"Duration mismatch. Expected: {expected_content['duration']}, Got: {result.duration}"
    )
    assert result.instrumental == expected_content["instrumental"], (
        f"Instrumental flag mismatch. Expected: {expected_content['instrumental']}, Got: {result.instrumental}"
    )
    assert result.plain_lyrics is not None, "Plain lyrics should not be None"
    assert result.synced_lyrics is not None, "Synced lyrics should not be None"
    assert result.plain_lyrics.startswith(expected_content["plainLyrics"]), (
        f"Plain lyrics don't start with expected content. Expected to start with: {expected_content['plainLyrics']}, Got: {result.plain_lyrics}"
    )
    assert result.synced_lyrics.startswith(expected_content["syncedLyrics"]), (
        f"Synced lyrics don't start with expected content. Expected to start with: {expected_content['syncedLyrics']}, Got: {result.synced_lyrics}"
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

    validate_get_result(result)


@my_vcr.use_cassette()
def test_get_lyrics_by_id(api: LrcLibAPI) -> None:
    result = api.get_lyrics_by_id(expected_content["id"])

    validate_get_result(result)


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
