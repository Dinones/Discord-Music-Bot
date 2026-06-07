###########################################################################################################################
#                                                                                                                         #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import re
import sys
import html
import difflib
import unicodedata
from typing import Optional, List, Tuple

import requests

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils import Constants as CONST
from Utils.Logs import save_exception_to_txt

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

# Matches LRC timestamp lines: [MM:SS], [MM:SS.xx], [MM:SS.xxx]
_LRC_LINE_RE = re.compile(r'^\[(\d{1,2}):(\d{2})(?:\.(\d{1,3}))?\](.*)')

# Common YouTube title noise: "(Official Video)", "(Lyric Video)", "(Letra)", "(Audio)", etc.
_TITLE_NOISE_RE = re.compile(
    r'\s*[\(\[](official\s*(music\s*)?video|lyric\s*video|letra|audio|hd|4k|official\s*audio|music\s*video)[\)\]]',
    re.IGNORECASE
)

# Matches the start-time portion of a VTT cue header: HH:MM:SS.mmm -->
_VTT_TIMESTAMP_RE = re.compile(r'^(\d{2}):(\d{2}):(\d{2})\.(\d{3})\s+-->')
# Strips inline word-level timing tags (<00:00:01.500>) and format tags (<c>, </c>, etc.)
_VTT_TAG_RE = re.compile(r'<[^>]+>')

_VTT_FETCH_TIMEOUT = 10

# Sync calibration thresholds
_SYNC_MIN_SIMILARITY = 0.6   # minimum SequenceMatcher ratio to accept a match
_SYNC_MAX_OFFSET     = 60.0  # seconds — discard implausible offsets (likely false match)
_SYNC_MIN_WORDS      = 2     # skip very short lyric lines that risk false positives

###########################################################################################################################
###########################################################################################################################

def parse_lrc(lrc_text: str) -> List[Tuple[float, str]]:

    """
    Parse an LRC-format lyrics string into a time-sorted list of (seconds, text) tuples.

    Args:
        lrc_text (str): Raw LRC string with timestamped lines.

    Returns:
        List[Tuple[float, str]]: Parsed lyrics sorted by timestamp ascending.
    """

    lines: List[Tuple[float, str]] = []

    for raw_line in lrc_text.splitlines():
        match = _LRC_LINE_RE.match(raw_line.strip())

        if not match:
            continue

        minutes  = int(match.group(1))
        seconds  = int(match.group(2))
        # Normalise fractional part to milliseconds (pad right to 3 digits)
        fraction = match.group(3) or "0"
        text     = match.group(4).strip()

        timestamp = minutes * 60.0 + seconds + int(fraction.ljust(3, "0")) / 1000.0
        lines.append((timestamp, text))

    return sorted(lines, key = lambda item: item[0])

###########################################################################################################################
###########################################################################################################################

def parse_vtt(vtt_text: str) -> List[Tuple[float, str]]:

    """
    Parse a WebVTT subtitle string into a time-sorted list of (seconds, text) tuples.
    Handles YouTube auto-generated captions by stripping word-level timing tags and
    deduplicating rolling-window lines.

    Args:
        vtt_text (str): Raw VTT string.

    Returns:
        List[Tuple[float, str]]: Parsed captions sorted by timestamp ascending.
    """

    lines     = vtt_text.splitlines()
    result    : List[Tuple[float, str]] = []
    last_text = ""
    i         = 0

    while i < len(lines):
        line  = lines[i].strip()
        match = _VTT_TIMESTAMP_RE.match(line)

        if not match:
            i += 1
            continue

        h  = int(match.group(1))
        m  = int(match.group(2))
        s  = int(match.group(3))
        ms = int(match.group(4))
        timestamp = h * 3600.0 + m * 60.0 + s + ms / 1000.0

        # Collect all text lines until the next blank separator line
        i += 1
        cue_lines: List[str] = []
        while i < len(lines) and lines[i].strip():
            cue_lines.append(lines[i].strip())
            i += 1

        # Strip all inline tags and decode HTML entities
        cleaned = [html.unescape(_VTT_TAG_RE.sub("", raw)).strip() for raw in cue_lines]
        cleaned = [l for l in cleaned if l]

        if not cleaned:
            continue

        # For rolling-window auto-captions, take the last non-empty line (the newest text)
        text = cleaned[-1]

        # Skip duplicate consecutive lines produced by rolling-window deduplication
        if text == last_text:
            continue

        last_text = text
        result.append((timestamp, text))

    return result

###########################################################################################################################
###########################################################################################################################

def get_current_lyric_line(lyrics: List[Tuple[float, str]], elapsed: float) -> str:

    """
    Return the lyric line whose timestamp is the closest one that does not exceed elapsed.

    Args:
        lyrics  (List[Tuple[float, str]]): Parsed lyrics from parse_lrc().
        elapsed (float): Current playback position in seconds.

    Returns:
        str: The active lyric line, or an empty string before the first timestamp.
    """

    current = ""

    for timestamp, text in lyrics:
        if timestamp <= elapsed:
            current = text
        else:
            break

    return current

###########################################################################################################################
###########################################################################################################################

def fetch_lyrics(title: str, artists: str, duration: int) -> Optional[List[Tuple[float, str]]]:

    """
    Fetch synced lyrics from LRClib for a given song. Tries a direct lookup first, then falls back to a search query
    when the direct lookup returns 404. Returns None for instrumental tracks or when synced lyrics are unavailable.

    Args:
        title    (str): Song title (YouTube title or Spotify track name).
        artists  (str): Comma-separated artist names; may be empty for YouTube-only songs.
        duration (int): Song duration in seconds; used by LRClib to disambiguate versions.

    Returns:
        Optional[List[Tuple[float, str]]]: Parsed synced lyrics, or None if unavailable.
    """

    title   = title.strip()
    artists = artists.strip()

    if not title:
        return None

    # Strip common YouTube video title noise before querying
    clean_title = _TITLE_NOISE_RE.sub("", title).strip()

    # Direct lookup requires artist_name — skip it for YouTube-only songs and go straight to search
    if artists:
        params: dict = {"track_name": clean_title, "artist_name": artists}
        if duration:
            params["duration"] = duration

        try:
            response = requests.get(
                url     = f"{CONST.LRCLIB_API_BASE_URL}/get",
                params  = params,
                timeout = CONST.LRCLIB_REQUEST_TIMEOUT
            )

            if response.status_code == 200:
                data   = response.json()
                synced = _extract_synced_lyrics(data)
                if synced is not None:
                    return synced
                # Found a match but no synced lyrics — do not bother searching
                return None

        except Exception as error:
            save_exception_to_txt(error = error, title = 'Lyrics_Fetch_Direct')
            return None

    # Fuzzy search — more forgiving with variant titles
    search_params: dict = {"track_name": clean_title}
    if artists:
        search_params["artist_name"] = artists

    try:
        search_response = requests.get(
            url     = f"{CONST.LRCLIB_API_BASE_URL}/search",
            params  = search_params,
            timeout = CONST.LRCLIB_REQUEST_TIMEOUT
        )

        if search_response.status_code != 200:
            return None

        results = search_response.json()

        if not isinstance(results, list):
            return None

        # Use the first result that has synced lyrics
        for result in results:
            synced = _extract_synced_lyrics(result)
            if synced is not None:
                return synced

        return None

    except Exception as error:
        save_exception_to_txt(error = error, title = 'Lyrics_Fetch_Search')
        return None

###########################################################################################################################
###########################################################################################################################

def fetch_youtube_captions(
    resolved_video : dict,
    ytdl_options   : Optional[dict] = None
) -> Optional[List[Tuple[float, str]]]:

    """
    Fetch and parse YouTube VTT captions from a yt-dlp resolved video entry. Used solely as a
    timing reference for sync calibration — the actual lyrics come from LRClib. Prefers manual
    subtitles over auto-generated captions, and English over other languages.

    When ytdl_options is provided the VTT file is fetched through yt-dlp's own HTTP session
    (cookies, User-Agent) to avoid YouTube 429 responses. Falls back to a plain requests.get
    call when ytdl_options is None (used in unit tests).

    Args:
        resolved_video (dict):          yt-dlp video info dict containing subtitle URLs under
                                        'subtitles' and/or 'automatic_captions'.
        ytdl_options   (Optional[dict]): yt-dlp options dict used to open the VTT URL through
                                        yt-dlp's authenticated session (default None).

    Returns:
        Optional[List[Tuple[float, str]]]: Parsed captions, or None if unavailable or on error.
    """

    url = _find_vtt_url(resolved_video)

    if not url:
        return None

    try:
        if ytdl_options is not None:
            from yt_dlp import YoutubeDL
            with YoutubeDL(ytdl_options) as ydl:
                vtt_text = ydl.urlopen(url).read().decode('utf-8', errors = 'replace')
        else:
            response = requests.get(url, timeout = _VTT_FETCH_TIMEOUT)
            if response.status_code != 200:
                return None
            vtt_text = response.text

        parsed = parse_vtt(vtt_text)
        return parsed if parsed else None

    except Exception as error:
        save_exception_to_txt(error = error, title = 'Captions_Fetch')
        return None

###########################################################################################################################
###########################################################################################################################

def calculate_lyric_sync_offset(
    lrc_lyrics   : List[Tuple[float, str]],
    vtt_captions : List[Tuple[float, str]]
) -> float:

    """
    Calculate the timing offset between LRClib lyrics and YouTube VTT captions by fuzzy-matching
    the first few lyric lines against caption text. Returns the value to ADD to all LRC timestamps
    to align them with the actual YouTube video timeline.

    Args:
        lrc_lyrics   (List[Tuple[float, str]]): Lyrics from LRClib (correct text, studio timing).
        vtt_captions (List[Tuple[float, str]]): Captions from YouTube (speech-to-text, video timing).

    Returns:
        float: Offset in seconds (positive = lyrics start later in video than in studio recording).
               Returns 0.0 when no reliable match is found.
    """

    if not lrc_lyrics or not vtt_captions:
        return 0.0

    # Normalise VTT once to avoid repeated work
    vtt_normalized = [
        (t, _normalize_text(text))
        for t, text in vtt_captions
        if text.strip()
    ]

    offsets: List[float] = []

    # Try the first several non-empty LRC lines — early lines are most reliable
    lrc_candidates = [
        (t, _normalize_text(text))
        for t, text in lrc_lyrics
        if text.strip()
    ][:5]

    for lrc_time, lrc_norm in lrc_candidates:
        # Skip very short lines that risk false-positive matches
        if len(lrc_norm.split()) < _SYNC_MIN_WORDS:
            continue

        best_ratio  = _SYNC_MIN_SIMILARITY - 0.001
        best_offset : Optional[float] = None

        for vtt_time, vtt_norm in vtt_normalized:
            ratio = difflib.SequenceMatcher(None, lrc_norm, vtt_norm).ratio()
            if ratio > best_ratio:
                best_ratio  = ratio
                best_offset = vtt_time - lrc_time

        if best_offset is not None and abs(best_offset) <= _SYNC_MAX_OFFSET:
            offsets.append(best_offset)

    if not offsets:
        return 0.0

    # Median is robust against the occasional bad match
    offsets.sort()
    return offsets[len(offsets) // 2]

###########################################################################################################################
###########################################################################################################################

def _extract_synced_lyrics(payload: dict) -> Optional[List[Tuple[float, str]]]:

    """
    Extract and parse the synced lyrics field from an LRClib response payload.

    Args:
        payload (dict): A single LRClib track response object.

    Returns:
        Optional[List[Tuple[float, str]]]: Parsed synced lyrics, or None if unavailable or instrumental.
    """

    if not isinstance(payload, dict):
        return None

    if payload.get("instrumental"):
        return None

    synced_text = (payload.get("syncedLyrics") or "").strip()

    if not synced_text:
        return None

    parsed = parse_lrc(synced_text)

    return parsed if parsed else None

###########################################################################################################################
###########################################################################################################################

def _find_vtt_url(resolved_video: dict) -> Optional[str]:

    """
    Find a VTT caption URL from a yt-dlp resolved video entry. Prefers manual subtitles
    over auto-generated captions.

    Args:
        resolved_video (dict): yt-dlp video info dict.

    Returns:
        Optional[str]: VTT URL, or None if no captions are available.
    """

    # Manual subtitles first (cleaner, no rolling-window deduplication needed)
    subtitles = resolved_video.get("subtitles") or {}
    if subtitles:
        url = _first_vtt_url(subtitles)
        if url:
            return url

    auto = resolved_video.get("automatic_captions") or {}
    return _first_vtt_url(auto)

###########################################################################################################################
###########################################################################################################################

def _first_vtt_url(captions: dict) -> Optional[str]:

    """
    Return the first VTT URL found in a subtitles or automatic_captions dict. Prefers English.

    Args:
        captions (dict): Dict mapping language codes to lists of format dicts.

    Returns:
        Optional[str]: First matching VTT URL, or None.
    """

    # Prefer English variants first
    for lang in ("en", "en-orig"):
        for fmt in captions.get(lang) or []:
            if isinstance(fmt, dict) and fmt.get("ext") == "vtt":
                return str(fmt.get("url", ""))

    # Fall back to any available language
    for formats in captions.values():
        for fmt in formats or []:
            if isinstance(fmt, dict) and fmt.get("ext") == "vtt":
                return str(fmt.get("url", ""))

    return None

###########################################################################################################################
###########################################################################################################################

def _normalize_text(text: str) -> str:

    """
    Lowercase, strip accents, and remove punctuation from text for fuzzy lyric matching.
    Converts accented characters to their ASCII equivalents so that LRClib text (correct
    accents) and YouTube speech-to-text (often missing accents) can still match.

    Args:
        text (str): Raw lyric or caption line.

    Returns:
        str: Normalized ASCII string containing only letters, digits, and spaces.
    """

    # NFKD decomposition separates base letters from accent marks
    decomposed = unicodedata.normalize('NFKD', text.lower())
    ascii_text = decomposed.encode('ascii', 'ignore').decode('ascii')
    return re.sub(r'[^a-z0-9\s]', '', ascii_text).strip()

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    pass
