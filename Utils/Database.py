###########################################################################################################################
#   SQLite database initialization and connection management for bot statistics.                                          #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import json
import os
import sys
import sqlite3
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Set

# Module may be executed for testing purposes and may require different import paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

DB_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Data", "stats.db"))

_SCHEMA = """
    CREATE TABLE IF NOT EXISTS stats (
        total_playing_seconds INTEGER NOT NULL DEFAULT 0,
        total_skips           INTEGER NOT NULL DEFAULT 0,
        active_days           INTEGER NOT NULL DEFAULT 0,
        last_join_date        TEXT
    );

    CREATE TABLE IF NOT EXISTS songs (
        url        TEXT    PRIMARY KEY,
        name       TEXT,
        play_count INTEGER NOT NULL DEFAULT 0,
        skip_count INTEGER NOT NULL DEFAULT 0,
        last_played TEXT
    );

    CREATE TABLE IF NOT EXISTS users (
        username         TEXT    PRIMARY KEY,
        songs_listened   INTEGER NOT NULL DEFAULT 0,
        seconds_listened INTEGER NOT NULL DEFAULT 0,
        songs_skipped    INTEGER NOT NULL DEFAULT 0,
        current_streak   INTEGER NOT NULL DEFAULT 0,
        peak_streak      INTEGER NOT NULL DEFAULT 0,
        last_active_date TEXT
    );

    CREATE TABLE IF NOT EXISTS song_requests (
        url           TEXT    NOT NULL REFERENCES songs(url),
        username      TEXT    NOT NULL,
        request_count INTEGER NOT NULL DEFAULT 0,
        PRIMARY KEY (url, username)
    );

    CREATE TABLE IF NOT EXISTS sessions (
        start_date   TEXT NOT NULL,
        end_date     TEXT,
        songs_played INTEGER NOT NULL DEFAULT 0,
        unique_users INTEGER NOT NULL DEFAULT 0,
        user_list    TEXT
    );
"""

_MIGRATIONS = [
    "ALTER TABLE stats ADD COLUMN total_skips INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE stats ADD COLUMN active_days INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE stats ADD COLUMN last_join_date TEXT",
    "ALTER TABLE songs ADD COLUMN skip_count INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE songs ADD COLUMN last_played TEXT",
    "ALTER TABLE users ADD COLUMN songs_skipped INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE users ADD COLUMN current_streak INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE users ADD COLUMN peak_streak INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE users ADD COLUMN last_active_date TEXT",
    "ALTER TABLE sessions ADD COLUMN user_list TEXT",
]

###########################################################################################################################
###########################################################################################################################

def _is_prod() -> bool:
    return os.environ.get('BOT_ENV', 'dev').strip().lower() == 'prod'

###########################################################################################################################
###########################################################################################################################

def get_connection() -> sqlite3.Connection:

    """
    Open and return a connection to the stats database. Creates the database file if it does not exist.

    Returns:
        sqlite3.Connection: Active SQLite connection with row_factory set to sqlite3.Row.
    """

    connection                = sqlite3.connect(DB_PATH)
    connection.row_factory    = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")

    return connection

###########################################################################################################################
###########################################################################################################################

def init_database() -> None:

    """
    Create all tables if they do not exist, seed the single stats row, and run column migrations.

    Returns:
        None
    """

    with get_connection() as connection:
        connection.executescript(_SCHEMA)

        if connection.execute("SELECT COUNT(*) FROM stats").fetchone()[0] == 0:
            connection.execute("INSERT INTO stats (total_playing_seconds) VALUES (0)")

        for migration in _MIGRATIONS:
            try:
                connection.execute(migration)
            except Exception:
                pass

###########################################################################################################################
###########################################################################################################################

def record_song_played(song: Dict[str, Any], played_seconds: int, users_in_vc: List[str]) -> None:

    """
    Record a completed song play in the database. No-op outside of the production environment.

    Args:
        song (Dict[str, Any]): Song item that just finished playing.
        played_seconds (int): Number of seconds the song was actively playing (excluding pauses).
        users_in_vc (List[str]): Usernames of non-bot members present in the voice channel.

    Returns:
        None
    """

    if not _is_prod():
        return

    url  = str(song.get("spotify_url") or song.get("playback_query") or "").strip()
    name = str(song.get("title", "")).strip()

    if not url:
        return

    today     = date.today().isoformat()
    yesterday = (date.today() - timedelta(days=1)).isoformat()

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO songs (url, name, play_count, last_played)
            VALUES (?, ?, 1, ?)
            ON CONFLICT(url) DO UPDATE SET
                name        = excluded.name,
                play_count  = play_count + 1,
                last_played = excluded.last_played
            """,
            (url, name, today)
        )

        if song.get("explicitly_requested"):
            requester = str(song.get("requested_by", "")).strip()
            if requester:
                connection.execute(
                    """
                    INSERT INTO song_requests (url, username, request_count)
                    VALUES (?, ?, 1)
                    ON CONFLICT(url, username) DO UPDATE SET
                        request_count = request_count + 1
                    """,
                    (url, requester)
                )

        connection.execute(
            "UPDATE stats SET total_playing_seconds = total_playing_seconds + ?",
            (played_seconds,)
        )

        for username in users_in_vc:
            row = connection.execute(
                "SELECT current_streak, last_active_date FROM users WHERE username = ?",
                (username,)
            ).fetchone()

            if row is None:
                new_streak     = 1
                update_streak  = True
            elif row["last_active_date"] == today:
                new_streak     = row["current_streak"]
                update_streak  = False
            elif row["last_active_date"] == yesterday:
                new_streak     = row["current_streak"] + 1
                update_streak  = True
            else:
                new_streak     = 1
                update_streak  = True

            if row is None:
                connection.execute(
                    """
                    INSERT INTO users (username, songs_listened, seconds_listened, current_streak, peak_streak, last_active_date)
                    VALUES (?, 1, ?, 1, 1, ?)
                    """,
                    (username, played_seconds, today)
                )
            elif update_streak:
                connection.execute(
                    """
                    UPDATE users SET
                        songs_listened   = songs_listened + 1,
                        seconds_listened = seconds_listened + ?,
                        current_streak   = ?,
                        peak_streak      = MAX(peak_streak, ?),
                        last_active_date = ?
                    WHERE username = ?
                    """,
                    (played_seconds, new_streak, new_streak, today, username)
                )
            else:
                connection.execute(
                    """
                    UPDATE users SET
                        songs_listened   = songs_listened + 1,
                        seconds_listened = seconds_listened + ?
                    WHERE username = ?
                    """,
                    (played_seconds, username)
                )

###########################################################################################################################
###########################################################################################################################

def record_song_skipped(url: str, skipper: str) -> None:

    """
    Increment the skip counters for a song and the user who triggered the skip.
    No-op outside of the production environment.

    Args:
        url (str): Canonical URL of the song being skipped.
        skipper (str): Username of the member who issued the skip command.

    Returns:
        None
    """

    if not _is_prod():
        return

    if not url:
        return

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO songs (url, skip_count) VALUES (?, 1)
            ON CONFLICT(url) DO UPDATE SET skip_count = skip_count + 1
            """,
            (url,)
        )

        connection.execute(
            """
            INSERT INTO users (username, songs_skipped) VALUES (?, 1)
            ON CONFLICT(username) DO UPDATE SET songs_skipped = songs_skipped + 1
            """,
            (skipper,)
        )

        connection.execute(
            "UPDATE stats SET total_skips = total_skips + 1"
        )

###########################################################################################################################
###########################################################################################################################

def record_bot_joined() -> None:

    """
    Increment the active-days counter once per calendar day. Safe to call on every voice-channel join;
    subsequent calls on the same day are ignored. No-op outside of the production environment.

    Returns:
        None
    """

    if not _is_prod():
        return

    today = date.today().isoformat()

    with get_connection() as connection:
        row = connection.execute("SELECT last_join_date FROM stats").fetchone()

        if row and row["last_join_date"] == today:
            return

        connection.execute(
            "UPDATE stats SET active_days = active_days + 1, last_join_date = ?",
            (today,)
        )

###########################################################################################################################
###########################################################################################################################

def record_session_end(start_dt: Optional[str], songs_played: int, users: Set[str]) -> None:

    """
    Write a completed session record to the database. No-op outside of the production environment
    or when start_dt is None (bot never entered prod-mode playback this session).

    Args:
        start_dt (Optional[str]): ISO datetime string when the session started.
        songs_played (int): Number of songs played during the session.
        users (Set[str]): Usernames of all unique users present during the session.

    Returns:
        None
    """

    if not _is_prod() or not start_dt:
        return

    end_dt    = datetime.now().isoformat(timespec='seconds')
    user_list = json.dumps(sorted(users))

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO sessions (start_date, end_date, songs_played, unique_users, user_list)
            VALUES (?, ?, ?, ?, ?)
            """,
            (start_dt, end_dt, songs_played, len(users), user_list)
        )

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    init_database()
    print(f"Database initialized at: {DB_PATH}")
