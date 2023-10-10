# LRCLibAPI

Python Wrapper for [lrclib.net](https://lrclib.net/) api to get synced lyrics.

<p>
  <a href="https://pypi.org/project/lrclibapi/">
    <img src="https://img.shields.io/pypi/v/lrclibapi?color=darkblue" alt="Stable Version">
  </a>
  <a href="https://pypistats.org/packages/lrclibapi">
    <img src="https://img.shields.io/pypi/dm/lrclibapi?color=teal" alt="Downloads">
  </a>
  <a href="https://github.com/Dr-Blank/lrclibapi/actions">
    <img src="https://github.com/Dr-Blank/lrclibapi/actions/workflows/tests.yaml/badge.svg" alt="Test">
  </a>
  <a href="https://github.com/psf/black">
    <img src="https://img.shields.io/badge/code%20style-black-000000.svg" alt="Code style: black">
  </a>
  <a href="https://mypy-lang.org/">
    <img src="https://www.mypy-lang.org/static/mypy_badge.svg" alt="Checked with mypy">
  </a>
</p>

## Installation

```bash
pip install lrclibapi
```

## Usage

```python
from lrclib import LrcLibAPI

# Create an instance of the API
api = LrcLibAPI(user_agent="my-app/0.0.1")

# Get lyrics for a track
lyrics = api.get_lyrics(
    track_name="I Want to Live",
    artist_name="Borislav Slavov",
    album_name="Baldur's Gate 3 (Original Game Soundtrack)",
    duration=233,
)

# Print the lyrics
print(lyrics.synced_lyrics or lyrics.plain_lyrics)

# Search for a lyrics
results = api.search_lyrics(
    track_name="I Want to Live",
)

# Print the results
for result in results:
    print(f"{result.artist_name} - {result.track_name} ({result.album_name})")

# Get lyrics by ID
lyrics = api.get_lyrics_by_id(lrclib_id=results[0].id)

# Print the lyrics
print(lyrics.synced_lyrics or lyrics.plain_lyrics)
```

## Features in Development

* [ ] Add cryptography challenge solver for posting lyrics
