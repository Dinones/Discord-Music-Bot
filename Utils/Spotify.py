###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import os
import sys
import asyncio
import requests
from time import time
from urllib.parse import urlparse
from typing import TYPE_CHECKING, TypedDict, Optional, Tuple, Dict, List, Any

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), f"../")))

# from Utils import Messages as MSG
from Utils import Constants as CONST
from Utils import Colored_Strings as STR
from Utils.AWS_Secrets import get_secrets
from Utils.Logs import save_exception_to_txt

if TYPE_CHECKING:
    from discord import Message

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

MODULE_NAME = 'Spotify'

SPOTIFY_AUTH_CACHE: Spotify_Secrets = {}

###########################################################################################################################
###########################################################################################################################

class Spotify_Secrets(TypedDict):

    """
    Typed structure to store the Spotify credentials and token metadata used by this module.
    """

    SPOTIFY_CLIENT_ID        : str
    SPOTIFY_CLIENT_SECRET    : str
    SPOTIFY_ACCESS_TOKEN     : str
    SPOTIFY_TOKEN_EXPIRES_AT : float

###########################################################################################################################
###########################################################################################################################

async def search_spotify_songs(message: Message, spotify_link: str) -> List[Dict[str, Any]]:

    """
    Searches for songs from a given Spotify link, handling tracks, albums, and playlists. It starts a child thread so the
    main Discord execution is not blocked. 

    Args:
        message (Message): The Discord message object containing user details.
        spotify_link (str): The Spotify link to process.

    Returns:
        List[Dict[str, Any]]: A list of song data dictionaries retrieved from the Spotify API.
    """

    return await asyncio.to_thread(_search_spotify_songs, message.author.name, spotify_link)

###########################################################################################################################
###########################################################################################################################

def _search_spotify_songs(user_name: str, spotify_link: str) -> List[Dict[str, Any]]:

    """
    Synchronous worker for Spotify lookups. It is executed in a thread so the async Discord loop does not block.

    Args:
        user_name (str): The Discord user name used in terminal log messages.
        spotify_link (str): The Spotify URL or path to resolve.

    Returns:
        List[Dict[str, Any]]: A list of Spotify track dictionaries, or an empty list when the lookup fails.
    """

    # Validate whether the link refers to a track, album, or playlist
    parsed_spotify_link = _parse_spotify_link(spotify_link)

    if not parsed_spotify_link:
        print(
            STR.G_ACTION_NOT_DONE.format(
                user   = user_name.capitalize(),
                action = 'play something from Spotify',
                reason = f'Request is not a song, album or playlist "{spotify_link}"'
            )
        )
        return []

    link_type, spotify_id = parsed_spotify_link

    # Obtain the Spotify auth token
    access_token = __craft_spotify_token()
    if not access_token:
        print(
            STR.G_ACTION_NOT_DONE
            .replace('{user}', user_name.capitalize())
            .replace('{action}', 'play something from Spotify')
            .replace('{reason}', 'Could not get a Spotify access token')
        )
        return []

    try:
        # Single tracks come back as one object, but playlists/albums need pagination and cleanup first
        if link_type == 'track':
            return [_fetch_spotify_track(spotify_id, access_token)]

        return _fetch_spotify_collection_tracks(link_type, spotify_id, access_token)

    except Exception as error:
        log_path = save_exception_to_txt(error = error, title = 'Spotify_Search')
        print(
            STR.G_ACTION_NOT_DONE
            .replace('{user}', user_name.capitalize())
            .replace('{action}', 'play something from Spotify')
            .replace('{reason}', str(error))
        )
        return []

###########################################################################################################################
###########################################################################################################################

def _parse_spotify_link(spotify_link: str) -> Optional[Tuple[str, str]]:

    """
    Extract the Spotify resource type and 22-character identifier from a Spotify web URL. Only accepts Spotify tracks,
    playlists and albums.

    Args:
        spotify_link (str): The Spotify URL provided by the user.

    Returns:
        Optional[Tuple[str, str]]: A `(link_type, spotify_id)` tuple when the link is valid, otherwise `None`.
    """

    spotify_link = spotify_link.strip()
    if not spotify_link:
        return None

    parsed_url = urlparse(spotify_link)

    if not is_spotify_url(spotify_link):
        return None

    path = parsed_url.path.strip('/')
    path_parts = [part for part in path.split('/') if part]

    # Spotify localized share links sometimes start with a language/region prefix such as "intl-es". That prefix only
    # affects the website route and raises an error when calling the Spotify API
    if path_parts and path_parts[0].startswith('intl-'):
        path_parts = path_parts[1:]

    # After normalization two path parts are expected: link_type and spotify_id
    if len(path_parts) < 2:
        return None

    # Supported link types: "track", "playlist" and "album"
    link_type, spotify_id = path_parts[0], path_parts[1]

    if link_type not in ('track', 'playlist', 'album'):
        return None

    # Spotify IDs are always 22 characters long
    if len(spotify_id) != 22:
        return None

    return link_type, spotify_id

###########################################################################################################################
###########################################################################################################################

def is_spotify_url(spotify_link: str) -> bool:

    """
    Validate whether a given input is a Spotify web URL.

    Args:
        spotify_link (str): User input link.

    Returns:
        bool: True when input is an HTTPS Spotify URL, otherwise False.
    """

    parsed_url = urlparse(spotify_link.strip())

    if parsed_url.scheme != 'https':
        return False

    return (parsed_url.hostname or '').lower() == 'open.spotify.com'

###########################################################################################################################
###########################################################################################################################

def _get_spotify_response(url: str, headers: Dict[str, str], params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:

    """
    Execute a Spotify API GET request and return a validated JSON payload.

    Args:
        url (str): The Spotify API endpoint to query.
        headers (Dict[str, str]): Request headers, including the Spotify bearer token.
        params (Optional[Dict[str, Any]]): Optional query parameters such as pagination controls and market.

    Returns:
        Dict[str, Any]: The decoded Spotify JSON payload.
    """

    try:
        response = requests.get(
            url     = url,
            headers = headers,
            params  = params,
            timeout = CONST.SPOTIFY_REQUEST_TIMEOUT
        )
    except requests.RequestException as error:
        log_path = save_exception_to_txt(error = error, title = 'Spotify_Get')
        raise Exception(f'Cannot reach the server "{url}" ({error})') from error

    # Any non-success status means the Spotify lookup failed with a user-friendly error message
    if response.status_code >= 400:
        error_text = (response.text or "").strip()
        error = Exception(
            f'Cannot reach the server (status code: {response.status_code}) "{url}": {error_text}'
        )
        log_path = save_exception_to_txt(error = error, title = 'Spotify_Get')
        raise error

    try:
        payload = response.json()
    except ValueError as error:
        log_path = save_exception_to_txt(error = error, title = 'Spotify_Get')
        raise Exception(f'Spotify returned an invalid response for "{url}"') from error

    if not isinstance(payload, dict):
        error = Exception(f'Spotify returned an unexpected payload for "{url}"')
        log_path = save_exception_to_txt(error = error, title = 'Spotify_Get')
        raise error

    return payload

###########################################################################################################################
###########################################################################################################################

def _fetch_spotify_track(spotify_id: str, access_token: str) -> dict:

    """
    Fetch and validate a single Spotify track payload.

    Args:
        spotify_id (str): The Spotify track identifier.
        access_token (str): A valid Spotify API bearer token.

    Returns:
        dict: The Spotify track payload.
    """

    track_url = f"https://api.spotify.com/v1/tracks/{spotify_id}"
    headers   = {"Authorization": f"Bearer {access_token}"}
    params    = {"market": CONST.SPOTIFY_DEFAULT_MARKET}
    payload   = _get_spotify_response(track_url, headers, params)

    if not payload.get('id'):
        error = Exception(f'Spotify returned an empty track response for "{track_url}": {payload}')
        log_path = save_exception_to_txt(error = error, title = 'Spotify_Fetch_Track')
        raise error

    return payload

###########################################################################################################################
###########################################################################################################################

def _fetch_spotify_collection_tracks(link_type: str, spotify_id: str, access_token: str) -> List[dict]:

    """
    Fetch every page of tracks for a Spotify album or playlist and normalize the payload into track dictionaries.

    Args:
        link_type (str): The Spotify resource type, either "album" or "playlist".
        spotify_id (str): The Spotify album or playlist identifier.
        access_token (str): A valid Spotify API bearer token.

    Returns:
        List[dict]: A normalized list of Spotify track dictionaries from the full collection.
    """

    tracks_url = (
        f"https://api.spotify.com/v1/playlists/{spotify_id}/items"
        if link_type == "playlist"
        else f"https://api.spotify.com/v1/albums/{spotify_id}/tracks"
    )
    headers    = {"Authorization": f"Bearer {access_token}"}
    params     = {"limit": 50, "offset": 0, "market": CONST.SPOTIFY_DEFAULT_MARKET}
    raw_tracks : List[Any] = []

    # Follow Spotify pagination until there is no "next" page left
    while tracks_url:
        payload = _get_spotify_response(tracks_url, headers, params)
        items   = payload.get('items')

        if not isinstance(items, list):
            error = Exception(f'Spotify returned an invalid tracks list for "{tracks_url}": {payload}')
            log_path = save_exception_to_txt(error = error, title = 'Spotify_Fetch_Collection_Tracks')
            raise error

        raw_tracks.extend(items)

        next_url   = payload.get('next')
        tracks_url = next_url if isinstance(next_url, str) and next_url else ''
        # After the request, Spotify's "next" URL already includes the right query string
        params = None

    songs: List[Dict[str, Any]] = []

    for track in raw_tracks:
        if link_type == 'playlist' and isinstance(track, dict):
            # Playlist items wrap the actual song payload under the "track" key
            track = track.get('track')

        # If Spotify removes a song, the request will return an empty track
        if not isinstance(track, dict) or not track.get('id'):
            continue

        songs.append(track)

    return songs

###########################################################################################################################
###########################################################################################################################

def __craft_spotify_token() -> str:

    """
    Crafts a Spotify access token using the client credentials flow. This function sends a POST request to Spotify's API to
    request an access token, which is required to access Spotify's web API. The token is cached in memory until it is close
    to expiring.

    Returns:
        str: The Spotify access token.
    """

    # Reuse the in-memory token while it is still valid to avoid unnecessary Spotify auth requests
    access_token = SPOTIFY_AUTH_CACHE.get("SPOTIFY_ACCESS_TOKEN", "")
    expires_at   = SPOTIFY_AUTH_CACHE.get("SPOTIFY_TOKEN_EXPIRES_AT", 0.0)

    if access_token and time() < expires_at:
        return access_token

    # Retrieve Spotify secrets from in-memory or AWS
    spotify_secrets = _get_spotify_secrets()

    if not spotify_secrets:
        # TODO: Print error log. Generate TXT is not necessary
        print(STR.SP_COULD_NOT_GET_TOKEN)
        return ''

    client_id     = spotify_secrets.get('SPOTIFY_CLIENT_ID', '')
    client_secret = spotify_secrets.get('SPOTIFY_CLIENT_SECRET', '')

    # Craft the Spotify access token
    token_url = "https://accounts.spotify.com/api/token"
    data      = {"grant_type" : "client_credentials"}
    auth      = (client_id, client_secret)

    # Query Spotify to get an access token
    try:
        response = requests.post(
            token_url,
            data    = data,
            auth    = auth, 
            timeout = CONST.SPOTIFY_REQUEST_TIMEOUT
        )
        payload = response.json()

    except Exception as error:
        log_path = save_exception_to_txt(error = error, title = 'Spotify_Token')
        print(STR.SP_COULD_NOT_GET_TOKEN)
        return ''

    access_token = payload.get("access_token", "")

    if not access_token:
        # TODO: Print error log "Spotify returned an empty access_token". Generate TXT is not necessary
        print(STR.SP_COULD_NOT_GET_TOKEN)
        return ''

    # Update the in-memory expiration date with the new one
    expires_in = payload.get("expires_in", 0)
    spotify_secrets["SPOTIFY_TOKEN_EXPIRES_AT"] = (
        time() + max(float(expires_in) - CONST.SPOTIFY_TOKEN_EXPIRATION_BUFFER_SECONDS, 0)
    )

    # Update the in-memory token
    spotify_secrets["SPOTIFY_ACCESS_TOKEN"] = access_token

    return spotify_secrets["SPOTIFY_ACCESS_TOKEN"]

###########################################################################################################################
###########################################################################################################################

def _get_spotify_secrets() -> Optional[Spotify_Secrets]:

    """
    Retrieve Spotify credentials from AWS Secrets Manager and cache them in memory after the first successful fetch.

    Returns:
        Optional[Spotify_Secrets]: Spotify cache dictionary if available, otherwise `None`.
    """

    if (
        SPOTIFY_AUTH_CACHE.get("SPOTIFY_CLIENT_ID", "") and
        SPOTIFY_AUTH_CACHE.get("SPOTIFY_CLIENT_SECRET", "")
    ):
        return SPOTIFY_AUTH_CACHE

    # Retrieve secrets from AWS
    spotify_secrets = get_secrets()
    if not spotify_secrets:
        return None

    if (
        not spotify_secrets.get("SPOTIFY_CLIENT_ID", "") or
        not spotify_secrets.get("SPOTIFY_CLIENT_SECRET", "")
    ):
        return None

    # Store secrets in-memory
    SPOTIFY_AUTH_CACHE["SPOTIFY_CLIENT_ID"]     = spotify_secrets.get("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_AUTH_CACHE["SPOTIFY_CLIENT_SECRET"] = spotify_secrets.get("SPOTIFY_CLIENT_SECRET", "")

    return SPOTIFY_AUTH_CACHE

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    import Debug.Spotify_Debug

    Debug.Spotify_Debug.main_menu()
