# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

PVARA AI Board Seat is an AI-powered autonomous voting system for Pakistan Virtual Asset Regulatory Authority (PVARA) board meetings. The system allows an AI Board Member to:
- Listen to board meetings in real-time via browser audio
- Understand motions and proposals using RAG (Retrieval Augmented Generation)
- Vote autonomously (FOR/AGAINST/ABSTAIN) with regulatory justification
- Reference PVARA regulations stored in Pinecone vector database

## Tech Stack

**Backend (Python/FastAPI):**
- FastAPI server with WebSocket support for real-time audio streaming
- OpenAI GPT-4o Realtime API for voice and decision-making
- Pinecone vector database for regulatory document retrieval
- OpenAI embeddings (text-embedding-3-small)
- JWT authentication with role-based access

**Frontend (React/TypeScript):**
- React 19 with TypeScript
- Vite build tool
- Tailwind CSS for styling
- LiveKit client for audio streaming
- WebSocket for real-time communication

## Development Commands

### Backend (Python)
```bash
# Setup virtual environment
python -m venv .venv
source .venv/bin/activate  # Mac/Linux
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run backend server (default port 5050)
python main.py

# Reset and re-ingest regulatory documents to Pinecone
python reset_and_ingest.py
```

### Frontend (React)
```bash
cd react-site

# Install dependencies
yarn install

# Run development server (port 5173)
yarn dev

# Build for production
yarn build

# Lint code
yarn lint

# Preview production build
yarn preview
```

## Environment Configuration

Required `.env` variables:
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
INDEX_NAME=pvara-docs
JWT_SECRET_KEY=your_jwt_secret_key
PORT=5050
```

## Architecture

### Backend Structure

**main.py** - FastAPI application entry point
- Defines all HTTP endpoints and WebSocket routes
- Handles authentication and JWT token generation
- Manages WebSocket connections to OpenAI Realtime API
- Orchestrates audio streaming pipeline (browser → server → OpenAI → browser)
- CORS configuration allows React dev server (ports 5173, 3000)

**tools.py** - Core business logic and function calling
- `retrieve_context()` - RAG retrieval from Pinecone using embeddings
- `cast_vote()` - AI voting logic with regulatory justification
- `add_motion()` - Motion tracking for voting
- `start_meeting_session()` / `end_meeting_session()` - Meeting lifecycle
- `get_vote_history()`, `get_transcript()` - Data retrieval
- In-memory storage: `meeting_sessions`, `vote_history`, `motion_queue`, `transcript_log`

**prompts.py** - AI system prompts and function definitions
- `build_system_message()` - Generates PVARA AI Board Member system prompt
- `function_call_tools` - OpenAI function calling schema for voting and retrieval
- Voice configuration (sage/shimmer/echo/onyx) with personality settings
- Gender-aware prompt generation

**utils.py** - Utility functions
- Audio conversion utilities
- Helper functions for data processing

**reset_and_ingest.py** - Document ingestion utility
- Reads .docx and .pdf files from `documents/` folder
- Chunks documents using RecursiveCharacterTextSplitter
- Generates embeddings and uploads to Pinecone
- Resets Pinecone index (deletes all vectors)
- Metadata structure: `source`, `text`, `chunk_index`, `uploaded_at`

### Frontend Structure

**src/App.tsx** - Main application component
- Manages authentication state and JWT tokens
- Orchestrates meeting lifecycle (start/stop, duration tracking)
- Handles WebSocket connections for audio streaming
- Coordinates between all child components
- Manages transcript buffering and display

**src/components/** - React components
- `LoginModal.tsx` - JWT authentication with role-based login
- `Header.tsx` - Shows user info, meeting status, duration timer
- `MeetingControls.tsx` - Start/stop meeting, mark motion for voting
- `AudioControls.tsx` - Microphone mute/unmute, recording indicator
- `AvatarContainer.tsx` - AI avatar visualization with status indicators
- `VoteResultCard.tsx` - Displays vote results with reasoning and regulatory references
- `Transcript.tsx` - Live meeting transcript display
- `ConnectionAlert.tsx` - WebSocket connection status alerts
- `QuickGuide.tsx` - User onboarding and help

**src/hooks/** - Custom React hooks
- `useAudioSession.ts` - Manages WebSocket audio streaming
- `useAudioPlayback.ts` - Handles audio playback from OpenAI

**src/utils/api.ts** - Axios wrapper for API calls with JWT auth

**src/types.ts** - TypeScript type definitions for shared data structures

### Key Data Flow

1. **Meeting Start**: Secretary starts meeting → creates meeting session in backend → establishes WebSocket connection
2. **Audio Streaming**: Browser captures audio → streams via WebSocket to FastAPI → forwards to OpenAI Realtime API
3. **Transcript**: OpenAI transcribes audio → sends back to server → broadcasts to React frontend
4. **Motion Voting**: Secretary marks motion → triggers `retrieve_context()` → AI analyzes with RAG → calls `cast_vote()` → returns structured vote
5. **Vote Display**: Vote result broadcast to frontend → displayed in VoteResultCard with full reasoning

### Authentication & Roles

Three user roles with different permissions:
- **Secretary**: Can start/stop meetings, mark voting items, view all data
- **Admin**: Full system access and configuration
- **Observer**: Read-only access to meetings and votes

JWT tokens stored in localStorage with 24-hour expiration.

Default credentials in `main.py` USERS_DB (lines 81-107).

### WebSocket Architecture

Two main WebSocket endpoints:
1. `/media-stream-browser` - Bidirectional audio streaming (browser ↔ server ↔ OpenAI)
2. OpenAI Realtime API connection - Server establishes separate WebSocket to OpenAI

Audio pipeline:
- Browser sends PCM audio (24kHz, base64 encoded)
- Server forwards to OpenAI as `input_audio_buffer.append` events
- OpenAI returns transcription and AI responses
- Server broadcasts back to browser for playback

### RAG (Retrieval Augmented Generation)

Regulatory documents stored in Pinecone vector database:
- Documents chunked with 1000 char chunks, 200 char overlap
- Embedded using OpenAI text-embedding-3-small
- Retrieved with semantic search (top_k=5 by default)
- Context injected into AI voting decisions

To add new regulatory documents:
1. Place .docx or .pdf files in `documents/` folder
2. Run `python reset_and_ingest.py`
3. Confirms ingestion with vector count

## Important Notes

- Backend must run before frontend (frontend makes API calls to localhost:5050)
- Pinecone index must be created before first run
- OpenAI Realtime API requires valid API key with sufficient credits
- WebSocket connections are stateful - ensure proper cleanup on disconnect
- In-memory storage means data resets on server restart (no database persistence)
- CORS is configured for local development only (ports 5173, 3000)

## Common Issues

**"Vector database not available"**: Check PINECONE_API_KEY and INDEX_NAME in .env

**WebSocket connection failed**: Ensure backend is running on port 5050 and OPENAI_API_KEY is valid

**Audio not streaming**: Check browser microphone permissions and WebSocket connection status

**Vote not triggering**: Ensure meeting is active and motion is properly marked by secretary
