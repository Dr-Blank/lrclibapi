"""Models for api.py"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, ClassVar, Dict, Generic, List, Optional, TypeVar

APIKey = TypeVar("APIKey", bound=str)

ModelAttr = TypeVar("ModelAttr", bound=str)

KeyMapping = Dict[APIKey, ModelAttr]

ModelT = TypeVar("ModelT", bound="BaseModel")


class BaseModel(Generic[ModelT]):
    """Base model"""

    _API_TO_MODEL_MAPPINGS: ClassVar[KeyMapping] = {}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> ModelT:
        """Create a ModelT object from a dictionary"""
        kwargs = {}
        for key, value in cls._API_TO_MODEL_MAPPINGS.items():
            kwargs[value] = data.get(key)
        return cls(**kwargs)  # type: ignore


@dataclass
class LyricsMinimal(BaseModel["LyricsMinimal"]):
    """Lyrics object with minimal information"""

    id: int  # pylint: disable=invalid-name
    name: str
    track_name: str
    artist_name: str
    album_name: str
    duration: int
    instrumental: bool
    plain_lyrics: Optional[str] = field(default=None, repr=False)
    synced_lyrics: Optional[str] = field(default=None, repr=False)

    _API_TO_MODEL_MAPPINGS: ClassVar[KeyMapping] = {
        "id": "id",
        "name": "name",
        "trackName": "track_name",
        "artistName": "artist_name",
        "albumName": "album_name",
        "duration": "duration",
        "instrumental": "instrumental",
        "plainLyrics": "plain_lyrics",
        "syncedLyrics": "synced_lyrics",
    }


@dataclass
class Lyrics(BaseModel["Lyrics"]):
    """Lyrics object with full information"""

    id: int  # pylint: disable=invalid-name
    name: str
    track_name: str
    artist_name: str
    album_name: str
    duration: int
    instrumental: bool
    """ if the lyrics are instrumental """
    plain_lyrics: Optional[str] = field(default=None, repr=False)
    synced_lyrics: Optional[str] = field(default=None, repr=False)
    lang: Optional[str] = field(default=None, repr=False)
    isrc: Optional[str] = field(default=None, repr=False)
    spotify_id: Optional[str] = field(default=None, repr=False)
    release_date: Optional[datetime] = field(default=None, repr=False)

    _API_TO_MODEL_MAPPINGS: ClassVar[KeyMapping] = {
        "id": "id",
        "name": "name",
        "trackName": "track_name",
        "artistName": "artist_name",
        "albumName": "album_name",
        "duration": "duration",
        "instrumental": "instrumental",
        "plainLyrics": "plain_lyrics",
        "syncedLyrics": "synced_lyrics",
        "lang": "lang",
        "isrc": "isrc",
        "spotifyId": "spotify_id",
        "releaseDate": "release_date",
    }

    def __post_init__(self):
        if self.release_date is not None:
            if not isinstance(self.release_date, str):
                return
            # 2023-08-10T00:00:00Z
            self.release_date = datetime.strptime(
                self.release_date, "%Y-%m-%dT%H:%M:%SZ"
            )


@dataclass
class ErrorResponse(BaseModel["ErrorResponse"]):
    """Response sent when an error occurs on the server"""

    status_code: int
    error: str
    message: str

    _API_TO_MODEL_MAPPINGS: ClassVar[KeyMapping] = {
        "statusCode": "status_code",
        "error": "error",
        "message": "message",
    }


class SearchResult(List[LyricsMinimal]):
    """list of LyricsMinimal objects"""

    def __init__(self, data: List[LyricsMinimal]) -> None:
        super().__init__(data)

    @classmethod
    def from_list(cls, data: List[Dict[str, Any]]) -> "SearchResult":
        """Create a SearchResult object from a list of dictionaries"""

        results = [LyricsMinimal.from_dict(result) for result in data]

        return cls(results)


@dataclass
class CryptographicChallenge(BaseModel["CryptographicChallenge"]):
    """Cryptographic Challenge"""

    prefix: str
    target: str

    _API_TO_MODEL_MAPPINGS: ClassVar[KeyMapping] = {
        "prefix": "prefix",
        "target": "target",
    }
