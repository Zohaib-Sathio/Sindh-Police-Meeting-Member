import sqlite3
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "meetings.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS meetings (
            meeting_id   TEXT PRIMARY KEY,
            start_time   TEXT NOT NULL,
            end_time     TEXT,
            duration_minutes INTEGER DEFAULT 0,
            agenda       TEXT DEFAULT '',
            status       TEXT DEFAULT 'active',
            total_votes  INTEGER DEFAULT 0,
            total_motions INTEGER DEFAULT 0,
            meeting_notes TEXT,
            created_at   TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS transcript_entries (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            meeting_id   TEXT NOT NULL,
            speaker      TEXT NOT NULL,
            text         TEXT NOT NULL,
            timestamp    TEXT NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
        );

        CREATE TABLE IF NOT EXISTS votes (
            id                   INTEGER PRIMARY KEY AUTOINCREMENT,
            vote_id              TEXT NOT NULL,
            meeting_id           TEXT NOT NULL,
            motion               TEXT NOT NULL,
            vote                 TEXT NOT NULL,
            reasoning            TEXT DEFAULT '',
            regulatory_reference TEXT DEFAULT '',
            risk_assessment      TEXT DEFAULT '',
            voter                TEXT DEFAULT '',
            timestamp            TEXT NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
        );

        CREATE TABLE IF NOT EXISTS motions (
            id           INTEGER PRIMARY KEY AUTOINCREMENT,
            motion_id    TEXT NOT NULL,
            meeting_id   TEXT NOT NULL,
            motion_text  TEXT NOT NULL,
            proposed_by  TEXT DEFAULT '',
            status       TEXT DEFAULT 'pending',
            timestamp    TEXT NOT NULL,
            FOREIGN KEY (meeting_id) REFERENCES meetings(meeting_id)
        );
    """)
    conn.commit()
    conn.close()
    print("✅ Database initialized")


def save_meeting_minutes(meeting_id, session_data, meeting_notes=None, duration_minutes=0):
    conn = get_connection()
    karachi_tz = ZoneInfo("Asia/Karachi")
    now = datetime.now(karachi_tz).isoformat()

    conn.execute("""
        INSERT OR REPLACE INTO meetings
        (meeting_id, start_time, end_time, duration_minutes, agenda, status,
         total_votes, total_motions, meeting_notes, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        meeting_id,
        session_data.get("start_time", now),
        session_data.get("end_time", now),
        duration_minutes,
        session_data.get("agenda", ""),
        "ended",
        len(session_data.get("votes", [])),
        len(session_data.get("motions", [])),
        meeting_notes,
        now,
    ))

    # Save transcript entries
    for entry in session_data.get("transcript", []):
        conn.execute("""
            INSERT INTO transcript_entries (meeting_id, speaker, text, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            meeting_id,
            entry.get("speaker", "Unknown"),
            entry.get("text", ""),
            entry.get("timestamp", now),
        ))

    # Save votes
    for v in session_data.get("votes", []):
        conn.execute("""
            INSERT INTO votes
            (vote_id, meeting_id, motion, vote, reasoning,
             regulatory_reference, risk_assessment, voter, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            v.get("vote_id", ""),
            meeting_id,
            v.get("motion", ""),
            v.get("vote", ""),
            v.get("reasoning", ""),
            v.get("regulatory_reference", ""),
            v.get("risk_assessment", ""),
            v.get("voter", ""),
            v.get("timestamp", now),
        ))

    # Save motions
    for m in session_data.get("motions", []):
        conn.execute("""
            INSERT INTO motions
            (motion_id, meeting_id, motion_text, proposed_by, status, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            m.get("motion_id", ""),
            meeting_id,
            m.get("motion_text", ""),
            m.get("proposed_by", ""),
            m.get("status", "pending"),
            m.get("timestamp", now),
        ))

    conn.commit()
    conn.close()
    print(f"✅ Meeting minutes saved to database: {meeting_id}")


def get_all_meetings():
    conn = get_connection()
    rows = conn.execute("""
        SELECT meeting_id, start_time, end_time, duration_minutes, agenda,
               status, total_votes, total_motions, created_at
        FROM meetings
        ORDER BY created_at DESC
    """).fetchall()
    conn.close()
    return [dict(r) for r in rows]


def get_meeting_minutes(meeting_id):
    conn = get_connection()

    meeting = conn.execute(
        "SELECT * FROM meetings WHERE meeting_id = ?", (meeting_id,)
    ).fetchone()
    if not meeting:
        conn.close()
        return None

    transcript = conn.execute(
        "SELECT speaker, text, timestamp FROM transcript_entries WHERE meeting_id = ? ORDER BY id",
        (meeting_id,)
    ).fetchall()

    votes = conn.execute(
        "SELECT vote_id, motion, vote, reasoning, regulatory_reference, risk_assessment, voter, timestamp "
        "FROM votes WHERE meeting_id = ? ORDER BY id",
        (meeting_id,)
    ).fetchall()

    motions = conn.execute(
        "SELECT motion_id, motion_text, proposed_by, status, timestamp "
        "FROM motions WHERE meeting_id = ? ORDER BY id",
        (meeting_id,)
    ).fetchall()

    conn.close()

    return {
        "meeting_id": meeting["meeting_id"],
        "start_time": meeting["start_time"],
        "end_time": meeting["end_time"],
        "duration_minutes": meeting["duration_minutes"],
        "agenda": meeting["agenda"],
        "status": meeting["status"],
        "total_votes": meeting["total_votes"],
        "total_motions": meeting["total_motions"],
        "meeting_notes": meeting["meeting_notes"],
        "transcript": [dict(r) for r in transcript],
        "votes": [dict(r) for r in votes],
        "motions": [dict(r) for r in motions],
    }
