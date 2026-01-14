"""
Sindh Police AI Meeting Member - Tools and Functions
Handles voting, operational context retrieval, and meeting management
"""

import os
import json
from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv

load_dotenv(override=True)


# In-memory storage for meeting data
meeting_sessions = {}
vote_history = []
transcript_buffer = []


def start_meeting_session(meeting_id: str, agenda: str = "") -> dict:
    """
    Start a new board meeting session.
    
    Args:
        meeting_id: Unique identifier for the meeting
        agenda: Optional agenda items for the meeting
        
    Returns:
        Meeting session details
    """
    karachi_tz = ZoneInfo("Asia/Karachi")
    now = datetime.now(karachi_tz)
    
    session = {
        "meeting_id": meeting_id,
        "status": "active",
        "start_time": now.isoformat(),
        "agenda": agenda,
        "transcript": [],
        "votes": [],
        "motions": []
    }
    
    meeting_sessions[meeting_id] = session
    print(f"✅ Meeting session started: {meeting_id}")
    
    return {
        "success": True,
        "message": f"Meeting session {meeting_id} started",
        "start_time": now.isoformat()
    }


def end_meeting_session(meeting_id: str) -> dict:
    """
    End an active board meeting session.
    
    Args:
        meeting_id: Unique identifier for the meeting
        
    Returns:
        Meeting summary
    """
    if meeting_id not in meeting_sessions:
        return {"success": False, "error": "Meeting session not found"}
    
    karachi_tz = ZoneInfo("Asia/Karachi")
    now = datetime.now(karachi_tz)
    
    session = meeting_sessions[meeting_id]
    session["status"] = "ended"
    session["end_time"] = now.isoformat()
    
    # Calculate duration
    start = datetime.fromisoformat(session["start_time"])
    duration = now - start
    
    summary = {
        "success": True,
        "meeting_id": meeting_id,
        "duration_minutes": int(duration.total_seconds() / 60),
        "total_votes": len(session["votes"]),
        "motions_discussed": len(session["motions"]),
        "end_time": now.isoformat()
    }
    
    print(f"✅ Meeting session ended: {meeting_id}")
    return summary


def cast_vote(
    meeting_id: str,
    motion_description: str,
    vote: str,
    reasoning: str,
    regulatory_reference: str,
    risk_assessment: str = ""
) -> dict:
    """
    Cast a vote on a motion during a board meeting.
    
    Args:
        meeting_id: Current meeting ID
        motion_description: Description of the motion
        vote: FOR, AGAINST, or ABSTAIN
        reasoning: Explanation for the vote
        regulatory_reference: Sindh Police policy/procedure supporting the vote
        risk_assessment: Optional risk implications
        
    Returns:
        Vote record
    """
    karachi_tz = ZoneInfo("Asia/Karachi")
    now = datetime.now(karachi_tz)
    
    # Validate vote
    if vote.upper() not in ["FOR", "AGAINST", "ABSTAIN"]:
        return {"success": False, "error": "Invalid vote. Must be FOR, AGAINST, or ABSTAIN"}
    
    vote_record = {
        "vote_id": f"VOTE-{now.strftime('%Y%m%d%H%M%S')}",
        "meeting_id": meeting_id,
        "timestamp": now.isoformat(),
        "motion": motion_description,
        "vote": vote.upper(),
        "reasoning": reasoning,
        "regulatory_reference": regulatory_reference,
        "risk_assessment": risk_assessment,
        "voter": "Sindh Police AI Meeting Member"
    }
    
    # Store vote
    vote_history.append(vote_record)
    
    # Add to meeting session if active
    if meeting_id in meeting_sessions:
        meeting_sessions[meeting_id]["votes"].append(vote_record)
    
    print(f"✅ Vote cast: {vote.upper()} on '{motion_description[:50]}...'")
    
    return {
        "success": True,
        "vote_record": vote_record
    }


def add_motion(meeting_id: str, motion_text: str, proposed_by: str = "Secretary") -> dict:
    """
    Add a motion for voting consideration.
    
    Args:
        meeting_id: Current meeting ID
        motion_text: The motion text
        proposed_by: Who proposed the motion
        
    Returns:
        Motion record
    """
    karachi_tz = ZoneInfo("Asia/Karachi")
    now = datetime.now(karachi_tz)
    
    motion_record = {
        "motion_id": f"MOTION-{now.strftime('%Y%m%d%H%M%S')}",
        "meeting_id": meeting_id,
        "timestamp": now.isoformat(),
        "motion_text": motion_text,
        "proposed_by": proposed_by,
        "status": "pending",
        "ai_vote": None
    }
    
    if meeting_id in meeting_sessions:
        meeting_sessions[meeting_id]["motions"].append(motion_record)
    
    print(f"📋 Motion added: {motion_text[:50]}...")
    
    return {
        "success": True,
        "motion_record": motion_record
    }


def get_meeting_status(meeting_id: str) -> dict:
    """
    Get the current status of a meeting session.
    
    Args:
        meeting_id: Meeting ID to check
        
    Returns:
        Meeting status and statistics
    """
    if meeting_id not in meeting_sessions:
        return {"success": False, "error": "Meeting not found"}
    
    session = meeting_sessions[meeting_id]
    
    return {
        "success": True,
        "meeting_id": meeting_id,
        "status": session["status"],
        "start_time": session["start_time"],
        "votes_cast": len(session["votes"]),
        "motions_pending": len([m for m in session["motions"] if m["status"] == "pending"]),
        "motions_voted": len([m for m in session["motions"] if m["status"] != "pending"])
    }


def get_vote_history(meeting_id: str = None) -> list:
    """
    Get vote history, optionally filtered by meeting.
    
    Args:
        meeting_id: Optional meeting ID to filter by
        
    Returns:
        List of vote records
    """
    if meeting_id:
        return [v for v in vote_history if v["meeting_id"] == meeting_id]
    return vote_history


def add_transcript_entry(meeting_id: str, speaker: str, text: str) -> dict:
    """
    Add a transcript entry to the meeting record.
    
    Args:
        meeting_id: Current meeting ID
        speaker: Who is speaking
        text: What was said
        
    Returns:
        Transcript entry
    """
    karachi_tz = ZoneInfo("Asia/Karachi")
    now = datetime.now(karachi_tz)
    
    entry = {
        "timestamp": now.isoformat(),
        "speaker": speaker,
        "text": text
    }
    
    if meeting_id in meeting_sessions:
        meeting_sessions[meeting_id]["transcript"].append(entry)
    
    transcript_buffer.append(entry)
    
    return {"success": True, "entry": entry}


def get_transcript(meeting_id: str) -> list:
    """
    Get the full transcript for a meeting.
    
    Args:
        meeting_id: Meeting ID
        
    Returns:
        List of transcript entries
    """
    if meeting_id in meeting_sessions:
        return meeting_sessions[meeting_id]["transcript"]
    return []


def request_regulatory_context(query: str) -> dict:
    """
    Request regulatory context for a specific topic or question.
    
    Args:
        query: The topic or question to search for
        
    Returns:
        Empty context (RAG feature removed)
    """
    return {
        "success": True,
        "query": query,
        "context": "RAG feature has been removed."
    }


# Export functions for use in main.py
__all__ = [
    'start_meeting_session',
    'end_meeting_session',
    'cast_vote',
    'add_motion',
    'get_meeting_status',
    'get_vote_history',
    'add_transcript_entry',
    'get_transcript',
    'request_regulatory_context',
    'meeting_sessions',
    'vote_history'
]
