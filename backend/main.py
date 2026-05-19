"""
FastAPI Backend for the Multi-Persona Chatroom
Serves both the API endpoints and the static frontend files.

Run with:
    uvicorn main:app --reload --port 8000

Then open http://localhost:8000 in your browser.
"""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from chat_engine import Conversation, get_persona_response
from personas import list_personas, PERSONAS


# ============================================================
# App setup
# ============================================================
app = FastAPI(title="Multi-Persona Chat API")

# Allow the browser to call the API from any origin (fine for local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory session store.
# Key = session_id (string), Value = Conversation object.
# For a class project this is fine; in production you would use Redis/a DB.
SESSIONS: dict[str, Conversation] = {}


# ============================================================
# Request / response models
# ============================================================
class NewSessionRequest(BaseModel):
    topic: str
    session_id: str  # frontend generates a UUID and sends it


class UserMessageRequest(BaseModel):
    session_id: str
    content: str


class PersonaSpeakRequest(BaseModel):
    session_id: str
    persona_id: str


class MessageOut(BaseModel):
    speaker_id: str
    speaker: str
    content: str
    avatar: Optional[str] = None
    color: Optional[str] = None


# ============================================================
# API endpoints
# ============================================================
@app.get("/api/personas")
def get_personas():
    """Return the list of available personas for the frontend."""
    return {"personas": list_personas()}


@app.post("/api/session/new")
def new_session(req: NewSessionRequest):
    """Create a new chat session with a topic."""
    SESSIONS[req.session_id] = Conversation(topic=req.topic)
    return {"session_id": req.session_id, "topic": req.topic}


@app.post("/api/session/user_message")
def user_message(req: UserMessageRequest):
    """Record the user's chimed-in message."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    conversation = SESSIONS[req.session_id]
    conversation.add_user_message(req.content)
    return {
        "speaker_id": "user",
        "speaker": "You",
        "content": req.content,
    }


@app.post("/api/session/persona_speak", response_model=MessageOut)
def persona_speak(req: PersonaSpeakRequest):
    """Let the chosen persona generate a reply."""
    if req.session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    if req.persona_id not in PERSONAS:
        raise HTTPException(status_code=404, detail="Persona not found")

    conversation = SESSIONS[req.session_id]
    persona = PERSONAS[req.persona_id]

    try:
        reply = get_persona_response(conversation, req.persona_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return MessageOut(
        speaker_id=req.persona_id,
        speaker=persona["name"],
        content=reply,
        avatar=persona.get("avatar"),
        color=persona.get("color"),
    )


@app.get("/api/session/{session_id}/history")
def get_history(session_id: str):
    """Get the full message history for a session (used when refreshing)."""
    if session_id not in SESSIONS:
        raise HTTPException(status_code=404, detail="Session not found")
    conversation = SESSIONS[session_id]

    # Enrich each message with avatar/color
    history = []
    for msg in conversation.history:
        item = dict(msg)
        if msg["speaker_id"] in PERSONAS:
            item["avatar"] = PERSONAS[msg["speaker_id"]]["avatar"]
            item["color"] = PERSONAS[msg["speaker_id"]]["color"]
        history.append(item)

    return {"topic": conversation.topic, "history": history}


# ============================================================
# Serve the frontend (must be mounted LAST, after all /api routes)
# ============================================================
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"

if FRONTEND_DIR.exists():
    @app.get("/")
    def serve_index():
        return FileResponse(FRONTEND_DIR / "index.html")

    # Mount remaining static files (CSS, JS) under root
    app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")
