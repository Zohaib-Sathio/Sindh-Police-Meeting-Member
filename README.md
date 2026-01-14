# PVARA AI Board Seat

AI-powered autonomous voting system for Pakistan Virtual Asset Regulatory Authority (PVARA) board meetings.

## Overview

This system provides an AI Board Member that can:
- **Listen** to board meetings in real-time via browser audio
- **Understand** motions and proposals using RAG (Retrieval Augmented Generation)
- **Vote** autonomously (FOR / AGAINST / ABSTAIN) with regulatory justification
- **Reference** PVARA regulations and guidelines for decision-making

## Features

### 🎤 Real-Time Meeting Listener
- Browser-based audio capture
- WebSocket streaming to OpenAI Realtime API
- Live transcription display

### 📋 Motion Detection & Voting
- Secretary marks agenda items for voting
- AI analyzes motion against PVARA regulations
- Automatic vote with justification and regulatory references

### 🔒 User Roles
- **Secretary**: Start/stop meetings, mark voting items, view all data
- **Admin**: Full system access and configuration
- **Observer**: Read-only access to meetings and votes

### 📊 Dashboard Features
- Meeting status and duration tracking
- Live transcript view
- AI connection status (Green/Yellow/Red)
- Vote result display with explanations
- Connection alerts

## Tech Stack

- **Backend**: FastAPI (Python)
- **AI**: OpenAI GPT-4o Realtime API
- **Vector DB**: Pinecone (for regulatory document retrieval)
- **Embeddings**: OpenAI text-embedding-3-small
- **Frontend**: HTML/JS with Tailwind CSS
- **Auth**: JWT tokens

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd "PVARA – AI Board Seat"
```

2. Create virtual environment:
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables (create `.env` file):
```env
OPENAI_API_KEY=your_openai_api_key
PINECONE_API_KEY=your_pinecone_api_key
INDEX_NAME=pvara-docs
JWT_SECRET_KEY=your_jwt_secret_key
PORT=5050
```

5. Run the application:
```bash
python main.py
```

6. Open browser: http://localhost:5050

## Default Credentials

| Role      | Username  | Password      |
|-----------|-----------|---------------|
| Secretary | secretary | secretary123  |
| Admin     | admin     | admin123      |
| Observer  | observer  | observer123   |

## API Endpoints

### Authentication
- `POST /auth/login` - User authentication

### Meeting Management
- `POST /api/meeting/start` - Start new meeting
- `POST /api/meeting/end` - End current meeting
- `GET /api/meeting/status` - Get meeting status

### Voting
- `POST /api/motion/add` - Add motion for voting
- `GET /api/votes/history` - Get vote history

### Regulatory Context
- `POST /api/context/query` - Query PVARA regulations

### Voice/Audio
- `POST /start-browser-call` - Initialize voice session
- `WS /media-stream-browser` - Audio WebSocket stream

### Health
- `GET /health` - System health check
- `GET /api/system/status` - Detailed system status

## Project Structure

```
PVARA – AI Board Seat/
├── main.py              # FastAPI application
├── prompts.py           # AI system prompts
├── tools.py             # Voting & RAG functions
├── utils.py             # Utility functions
├── requirements.txt     # Python dependencies
├── .env                 # Environment variables
├── static/
│   └── voice-client.html   # Secretary Dashboard
└── documents/           # PVARA regulatory documents
```

## Voting Logic

The AI Board Member evaluates motions based on:

1. **Legal Compliance** - Alignment with PVARA regulations
2. **Investor Protection** - Safeguards for virtual asset users
3. **Market Integrity** - Fair and transparent market practices
4. **Innovation Balance** - Responsible innovation allowance
5. **Risk Assessment** - Potential risks and mitigations

### Vote Types
- **FOR** - Motion aligns with regulatory objectives
- **AGAINST** - Motion contradicts regulations or lacks safeguards
- **ABSTAIN** - Insufficient information or conflict of interest

## License

Proprietary - PVARA Internal Use Only
