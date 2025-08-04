""" Tests for the API models. """

from datetime import datetime

from lrclibapi.models import (
    Lyrics,
    LyricsMinimal,
    ErrorResponse,
    SearchResult,
    CryptographicChallenge,
)

minimal_lyrics = {
    "id": 123,
    "name": "test_name",
    "trackName": "test_track_name",
    "artistName": "test_artist_name",
    "albumName": "test_album_name",
    "duration": 180,
    "instrumental": False,
    "plainLyrics": "test_plain_lyrics",
    "syncedLyrics": "test_synced_lyrics",
}

full_lyrics = {
    **minimal_lyrics,
    "lang": "test_lang",
    "isrc": "test_isrc",
    "spotifyId": "test_spotify_id",
    "releaseDate": "2023-08-10T00:00:00Z",
}

sample_search_result = [minimal_lyrics, minimal_lyrics]


def test_lyrics_minimal_from_dict() -> None:
    """Test the LyricsMinimal.from_dict method"""
    # Create a LyricsMinimal object from a dictionary
    lyrics = LyricsMinimal.from_dict(minimal_lyrics)

    # Check that the LyricsMinimal object has the expected type
    assert isinstance(lyrics, LyricsMinimal)

    # Check that the LyricsMinimal object has the expected attributes
    assert lyrics.id == minimal_lyrics["id"]
    assert lyrics.name == minimal_lyrics["name"]
    assert lyrics.track_name == minimal_lyrics["trackName"]
    assert lyrics.artist_name == minimal_lyrics["artistName"]
    assert lyrics.album_name == minimal_lyrics["albumName"]
    assert lyrics.duration == minimal_lyrics["duration"]
    assert lyrics.instrumental == minimal_lyrics["instrumental"]
    assert lyrics.plain_lyrics == minimal_lyrics["plainLyrics"]
    assert lyrics.synced_lyrics == minimal_lyrics["syncedLyrics"]


def test_lyrics_from_dict() -> None:
    lyrics = Lyrics.from_dict(full_lyrics)

    assert isinstance(lyrics, Lyrics)

    assert lyrics.id == full_lyrics["id"]
    assert lyrics.name == full_lyrics["name"]
    assert lyrics.track_name == full_lyrics["trackName"]
    assert lyrics.artist_name == full_lyrics["artistName"]
    assert lyrics.album_name == full_lyrics["albumName"]
    assert lyrics.duration == full_lyrics["duration"]
    assert lyrics.instrumental == full_lyrics["instrumental"]
    assert lyrics.plain_lyrics == full_lyrics["plainLyrics"]
    assert lyrics.synced_lyrics == full_lyrics["syncedLyrics"]
    assert lyrics.lang == full_lyrics["lang"]
    assert lyrics.isrc == full_lyrics["isrc"]
    assert lyrics.spotify_id == full_lyrics["spotifyId"]
    assert lyrics.release_date == datetime(2023, 8, 10, 0, 0, 0)


def test_lyrics_from_dict_with_proper_release_date() -> None:
    lyrics = Lyrics.from_dict(full_lyrics)
    lyrics_proper = Lyrics(**lyrics.__dict__)
    assert lyrics_proper.release_date == datetime(2023, 8, 10, 0, 0, 0)


def test_error_response_from_dict() -> None:
    error_response = ErrorResponse.from_dict(
        {"error": "test_error", "message": "test_message"}
    )

    assert isinstance(error_response, ErrorResponse)

    assert error_response.error == "test_error"
    assert error_response.message == "test_message"


def test_search_result_from_dict() -> None:
    search_result = SearchResult.from_list(sample_search_result)

    assert isinstance(search_result, SearchResult)

    assert len(search_result) == len(sample_search_result)

    for lyrics in search_result:
        assert isinstance(lyrics, LyricsMinimal)


def test_cryptographic_challenge_from_dict() -> None:
    challenge = CryptographicChallenge.from_dict(
        {"prefix": "test_prefix", "target": "test_target"}
    )

    assert isinstance(challenge, CryptographicChallenge)

    assert challenge.prefix == "test_prefix"
    assert challenge.target == "test_target"
