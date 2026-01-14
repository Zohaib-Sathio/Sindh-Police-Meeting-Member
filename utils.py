"""
Sindh Police AI Meeting Member - Utility Functions
"""

import uuid
import io
from pydub import AudioSegment
import audioop
from datetime import timezone, timedelta
import datetime


try:
    import pyaudio
except ImportError:
    pyaudio = None

CHUNK = 1024
if pyaudio:
    FORMAT = pyaudio.paInt16  # 16-bit PCM
else:
    FORMAT = None
CHANNELS = 1
RATE = 8000


def generate_call_id():
    """Generate a unique call/session ID."""
    return str(uuid.uuid4())


def get_total_duration_ms(events):
    """Return total duration in milliseconds based on recorded events."""
    if not events:
        return 0
    last_offset = max(offset for offset, _ in events)
    chunk_duration_ms = int((CHUNK / RATE) * 1000)
    total = int(last_offset * 1000) + chunk_duration_ms
    return total


def merge_timeline_events(events, total_duration_ms):
    """
    Create a full-length AudioSegment by overlaying each audio chunk at its proper offset.
    The events list is sorted by timestamp before overlay.
    """
    base = AudioSegment.silent(duration=total_duration_ms, frame_rate=RATE)
    sorted_events = sorted(events, key=lambda x: x[0])
    
    for offset, audio_data in sorted_events:
        try:
            pcm_audio = audioop.ulaw2lin(audio_data, 2)
            seg = AudioSegment.from_raw(
                io.BytesIO(pcm_audio), 
                frame_rate=RATE, 
                channels=1, 
                sample_width=2
            )
            base = base.overlay(seg, position=int(offset * 1000))
        except Exception as e:
            print(f"Error overlaying chunk at {offset:.2f} sec: {e}")
    return base


def make_filenames(call_id):
    """Generate recording filenames for a call/session."""
    return (
        f"call_{call_id}_incoming.wav",
        f"call_{call_id}_outgoing.wav",
        f"call_{call_id}_merged.wav"
    )


def format_duration(seconds: int) -> str:
    """Format seconds into HH:MM:SS string."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_timestamp(dt_obj: datetime.datetime = None) -> str:
    """Format datetime to ISO string."""
    if dt_obj is None:
        dt_obj = datetime.datetime.now(timezone.utc)
    return dt_obj.isoformat()
