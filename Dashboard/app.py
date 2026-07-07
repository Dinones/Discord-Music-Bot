###########################################################################################################################
#   Flask dashboard for visualizing bot stats from the SQLite database.                                                   #
###########################################################################################################################

###########################################################################################################################
####################################################     LIBRARIES     ####################################################
###########################################################################################################################

from __future__ import annotations

import csv
import os
import sys
import json
from datetime import datetime
from typing import Optional
from flask import Flask, render_template, Response, redirect

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from Utils.Database import get_connection

###########################################################################################################################
#################################################     INITIALIZATIONS     #################################################
###########################################################################################################################

app = Flask(__name__)

_TOP_LIMIT     = 10
_SESSION_LIMIT = 3
_SKIP_LIMIT    = 7

###########################################################################################################################
###########################################################################################################################

def _format_duration(seconds: int) -> str:

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h:
        return f"{h}h {m}m"
    if m:
        return f"{m}m {s}s"
    return f"{s}s"

###########################################################################################################################
###########################################################################################################################

def _truncate(text: str, max_len: int = 35) -> str:
    return text if len(text) <= max_len else text[:max_len - 1] + "…"

###########################################################################################################################
###########################################################################################################################

def _cap(text: str) -> str:
    return text[:1].upper() + text[1:] if text else text

###########################################################################################################################
###########################################################################################################################

def _session_duration(start: Optional[str], end: Optional[str]) -> str:

    if not start or not end:
        return "—"

    try:
        seconds = int((datetime.fromisoformat(end) - datetime.fromisoformat(start)).total_seconds())
        return _format_duration(max(0, seconds))
    except Exception:
        return "—"

###########################################################################################################################
###########################################################################################################################

def _load_stats() -> dict:

    try:
        conn = get_connection()

        row           = conn.execute("SELECT total_playing_seconds, active_days FROM stats").fetchone()
        total_seconds = row["total_playing_seconds"] if row else 0
        active_days   = row["active_days"]            if row else 0

        total_plays   = conn.execute(
            "SELECT COALESCE(SUM(play_count), 0) FROM songs"
        ).fetchone()[0]
        unique_songs  = conn.execute(
            "SELECT COUNT(*) FROM songs"
        ).fetchone()[0]

        top_songs = conn.execute(
            "SELECT name, play_count FROM songs ORDER BY play_count DESC LIMIT ?",
            (_TOP_LIMIT,)
        ).fetchall()

        top_skipped = conn.execute(
            "SELECT name, skip_count FROM songs WHERE skip_count > 0 ORDER BY skip_count DESC LIMIT ?",
            (_SKIP_LIMIT,)
        ).fetchall()

        top_users = conn.execute(
            "SELECT username, songs_listened, seconds_listened FROM users ORDER BY songs_listened DESC LIMIT ?",
            (_TOP_LIMIT,)
        ).fetchall()

        user_streaks = conn.execute(
            "SELECT username, current_streak, peak_streak, songs_skipped FROM users ORDER BY peak_streak DESC LIMIT ?",
            (_TOP_LIMIT,)
        ).fetchall()

        top_requests = conn.execute(
            """
            SELECT s.name, sr.username, sr.request_count
            FROM song_requests sr
            JOIN songs s ON s.url = sr.url
            ORDER BY sr.request_count DESC
            LIMIT ?
            """,
            (_TOP_LIMIT,)
        ).fetchall()

        recent_sessions = conn.execute(
            "SELECT start_date, end_date, songs_played, unique_users FROM sessions ORDER BY start_date DESC LIMIT ?",
            (_SESSION_LIMIT,)
        ).fetchall()

        activity_rows = conn.execute(
            "SELECT DATE(start_date) as day, MAX(unique_users) as max_users "
            "FROM sessions GROUP BY DATE(start_date)"
        ).fetchall()
        activity_sessions = conn.execute(
            "SELECT DATE(start_date) as day, user_list FROM sessions WHERE user_list IS NOT NULL"
        ).fetchall()
        activity_max = conn.execute(
            "SELECT COALESCE(MAX(unique_users), 1) FROM sessions"
        ).fetchone()[0]

        _day_users: dict = {}
        for r in activity_sessions:
            try:
                names = json.loads(r["user_list"] or "[]")
            except Exception:
                names = []
            _day_users.setdefault(r["day"], set()).update(names)

        activity_data = {
            r["day"]: {
                "count": r["max_users"],
                "users": sorted(_day_users.get(r["day"], set()))
            }
            for r in activity_rows
        }

        conn.close()

    except Exception:
        total_seconds = total_plays = active_days = unique_songs = 0
        top_songs = top_skipped = top_users = user_streaks = top_requests = recent_sessions = []
        activity_data = {}
        activity_max  = 1

    return {
        # Overview
        "total_time"        : _format_duration(total_seconds),
        "total_plays"       : total_plays,
        "unique_songs"      : unique_songs,
        "active_days"       : active_days,

        # Songs
        "songs_labels"      : json.dumps([_truncate(_cap(r["name"] or "Unknown")) for r in top_songs]),
        "songs_data"        : json.dumps([r["play_count"] for r in top_songs]),
        "top_skipped"       : [
            {"song": _truncate(_cap(r["name"] or "Unknown"), 50), "count": r["skip_count"]}
            for r in top_skipped
        ],

        # Users
        "users_labels"      : json.dumps([r["username"].capitalize() for r in top_users]),
        "users_songs_data"  : json.dumps([r["songs_listened"] for r in top_users]),
        "users_time_labels" : json.dumps([_format_duration(r["seconds_listened"]) for r in top_users]),
        "user_streaks"      : [
            {
                "username"       : r["username"].capitalize(),
                "current_streak" : r["current_streak"],
                "peak_streak"    : r["peak_streak"],
                "songs_skipped"  : r["songs_skipped"],
            }
            for r in user_streaks
        ],

        # Sessions
        "sessions"          : [
            {
                "date"     : r["start_date"][:10],
                "duration" : _session_duration(r["start_date"], r["end_date"]),
                "songs"    : r["songs_played"],
                "users"    : r["unique_users"],
            }
            for r in recent_sessions
        ],
        "activity_data"     : json.dumps(activity_data),
        "activity_max"      : activity_max,

        # Requests
        "requests"          : [
            {
                "song"  : _truncate(_cap(r["name"] or "Unknown"), 55),
                "user"  : r["username"].capitalize(),
                "count" : r["request_count"]
            }
            for r in top_requests
        ],
    }

###########################################################################################################################
#################################################     ROUTES     ########################################################
###########################################################################################################################

@app.route("/")
def dashboard() -> str:
    return render_template("index.html", **_load_stats())

###########################################################################################################################
###########################################################################################################################

_EXPORT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "Media", "Data"))

_EXPORT_TABLES = [
    ("stats",         "SELECT * FROM stats"),
    ("songs",         "SELECT * FROM songs ORDER BY play_count DESC"),
    ("users",         "SELECT * FROM users ORDER BY songs_listened DESC"),
    ("sessions",      "SELECT * FROM sessions ORDER BY start_date DESC"),
    ("song_requests", "SELECT * FROM song_requests ORDER BY request_count DESC"),
]

@app.route("/export")
def export_csv() -> Response:

    timestamp  = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    export_dir = os.path.join(_EXPORT_DIR, timestamp)
    os.makedirs(export_dir, exist_ok = True)

    conn = get_connection()

    for table_name, query in _EXPORT_TABLES:
        rows = conn.execute(query).fetchall()
        if not rows:
            continue
        with open(os.path.join(export_dir, f"{table_name}.csv"), "w", newline = "", encoding = "utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(rows[0].keys())
            writer.writerows(list(r) for r in rows)

    conn.close()

    return redirect("/")

###########################################################################################################################
#####################################################     PROGRAM     #####################################################
###########################################################################################################################

if __name__ == "__main__":
    app.run(debug = True, port = 5050)
