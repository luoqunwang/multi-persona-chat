# Multi-Persona AI Chatroom

An AI-powered web application that allows users to host conversations between historical figures — Socrates, Lu Xun, and Albert Einstein — and join the discussion themselves. Built as the final project for DIGS 20006/30006 *Artificial Intelligence and the Humanities* at the University of Chicago.

The system is a research probe for examining how large language models simulate deceased historical figures: what gets preserved, what gets lost, and what gets quietly invented.

## Background

This project sits at the intersection of generative AI and the humanities. It draws on Amy Kurzweil's concept of "chatbots of the dead" (Kurzweil 2025), Henry Farrell's framing of large language models as "cultural technologies" (Farrell 2025), and the ongoing debate about hallucination, sycophancy, and authenticity in AI-generated content.

Rather than treating the chatbot as a finished product, the project uses it as an instrument to ask three questions:

1. **Authenticity** — How faithfully can a language model represent a historical figure whose corpus is limited, translated, or filtered through centuries of interpretation?
2. **Representation** — When the model produces confident statements about what a figure believed, what cultural assumptions are being smuggled in?
3. **Limits of machine-generated identity** — What is preserved when an LLM imitates a style, and what is quietly replaced?

## Features

- Conversation interface with three historical personas, each defined by a detailed system prompt
- Multi-party context management that lets each persona track what the others have said
- User can interject at any point with a question or counter-argument
- A "let everyone speak" mode that runs the personas in sequence on the same topic
- Per-persona visual styling (color, avatar) to keep the conversation readable
- Built-in retry logic for transient API failures (rate limits and server load)

## Technical Architecture

- **Backend**: Python, FastAPI
- **Frontend**: Vanilla HTML, CSS, JavaScript (no framework dependencies)
- **Language Model**: Google Gemini 2.5 Flash-Lite (via the official Google GenAI SDK)
- **Deployment**: Render.com (web service), GitHub (source control)

The conversation engine wraps each persona's history into Gemini's two-role API by relabeling the active persona's prior messages as `model` and everyone else's (including the human user) as `user`, with a `[Speaker Name]` tag prepended. This per-speaker reframing is what allows four distinct voices to share one coherent conversation.

## Project Structure

```
multi-persona-chat-gemini/
├── backend/
│   ├── personas.py          System prompts for each persona
│   ├── chat_engine.py       Conversation state and Gemini API calls
│   ├── terminal_chat.py     CLI version for prompt development
│   └── main.py              FastAPI server and REST endpoints
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt
├── render.yaml              Deployment configuration
├── .env.example             Template for API key configuration
└── .gitignore
```

## Local Setup

### Prerequisites

- Python 3.10 or higher
- A Google Gemini API key (free tier; sign up at https://aistudio.google.com/)

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/luoqunwang/multi-persona-chat.git
   cd multi-persona-chat
   ```

2. Create and activate a virtual environment:
   ```
   python -m venv venv
   venv\Scripts\Activate.ps1     # Windows PowerShell
   source venv/bin/activate      # macOS / Linux
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Configure your API key:
   ```
   copy .env.example .env        # Windows
   cp .env.example .env          # macOS / Linux
   ```
   Open `.env` and replace the placeholder with your Gemini API key:
   ```
   GEMINI_API_KEY=your_key_here
   ```

5. Start the web server:
   ```
   cd backend
   uvicorn main:app --reload --port 8000
   ```

6. Open http://localhost:8000 in a browser.

### Terminal Version

For prompt engineering and quick testing without the web UI:

```
cd backend
python terminal_chat.py
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET    | `/api/personas`                       | List available personas |
| POST   | `/api/session/new`                    | Start a new conversation session |
| POST   | `/api/session/user_message`           | Record a user message |
| POST   | `/api/session/persona_speak`          | Generate a reply from a chosen persona |
| GET    | `/api/session/{session_id}/history`   | Retrieve full conversation history |

Sessions are stored in-memory and are not persisted between server restarts.

## Notes on Free-Tier Limits

The system defaults to `gemini-2.5-flash-lite`, which offers the largest free-tier quota (15 requests per minute, 1,000 per day). For higher-quality output during a final demo, the model can be changed to `gemini-2.5-flash` or `gemini-2.5-pro` in `backend/chat_engine.py`. Note that free-tier conversations may be used by Google to improve the model — a limitation worth flagging when deploying for public use.

## Course Context

DIGS 20006/30006, *Artificial Intelligence and the Humanities*
Instructor: Jeffrey Tharsen
University of Chicago, Spring 2026

This project addresses several concepts from the course, including hallucination (Swain 2025; OpenAI 2025), sycophancy (Malmquist 2024), simulated awareness versus awareness (Hayles 2024), large language models as cultural technologies (Farrell 2025), and chatbots of the dead (Kurzweil 2025).

## License

This project is for academic coursework. The persona system prompts draw on publicly available biographical and philosophical information about the historical figures depicted. All Gemini-generated content remains subject to Google's terms of service.