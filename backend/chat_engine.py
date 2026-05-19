"""
Chat Engine (Gemini version)
Responsibilities:
1. Maintain conversation history
2. Build the correct context for each persona (wrap others' speech as user messages)
3. Call the Gemini API to get responses
"""

import os
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import types

from personas import get_persona, PERSONAS

# Load environment variables from the .env file.
# Explicitly point to the project root (one level above /backend).
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=ROOT_DIR / ".env")

# Initialize the Gemini client
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found!\n"
        "Please verify:\n"
        "  1. There is a .env file in the PROJECT ROOT (not in /backend)\n"
        "  2. The contents look like: GEMINI_API_KEY=your_key (no quotes, no spaces)\n"
        "  3. You created a key at https://aistudio.google.com/\n"
    )

client = genai.Client(api_key=API_KEY)

# Model selection:
# - "gemini-2.5-flash-lite": Largest free quota (15 RPM / 1000 RPD). Best for development.
# - "gemini-2.5-flash":      Better quality, but only 10 RPM / 250 RPD; can hit 503s.
# - "gemini-2.5-pro":        Best quality, but only 5 RPM / 100 RPD; use for the final demo.
MODEL_NAME = "gemini-2.5-flash-lite"


class Conversation:
    """
    Conversation state manager.

    history format: [{"speaker": "Socrates", "speaker_id": "socrates", "content": "..."}, ...]
    A speaker_id of "user" represents the real human user.
    """

    def __init__(self, topic: str = ""):
        self.topic = topic
        self.history: list[dict] = []

    def add_message(self, speaker_id: str, speaker_name: str, content: str):
        """Append a message to the history."""
        self.history.append({
            "speaker_id": speaker_id,
            "speaker": speaker_name,
            "content": content,
        })

    def add_user_message(self, content: str):
        """The real user chimes in."""
        self.add_message("user", "User", content)

    def format_for_persona(self, persona_id: str) -> list:
        """
        Format the conversation history into Gemini's `contents` format.

        Key trick: Gemini's API only accepts two roles: "user" and "model".
        We map the *current* persona's previous lines to role="model",
        and everyone else's lines (other personas + the real user) to role="user",
        prefixing each with a [Speaker Name] tag so the model knows who said what.
        """
        contents = []
        for msg in self.history:
            if msg["speaker_id"] == persona_id:
                # The current persona's own previous lines -> role=model
                contents.append(
                    types.Content(
                        role="model",
                        parts=[types.Part.from_text(text=msg["content"])],
                    )
                )
            else:
                # Everyone else -> role=user, with [Speaker] tag
                contents.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_text(
                            text=f"[{msg['speaker']}]: {msg['content']}"
                        )],
                    )
                )

        # Gemini requires `contents` to start with a user message
        if not contents or contents[0].role != "user":
            contents.insert(0, types.Content(
                role="user",
                parts=[types.Part.from_text(
                    text=f"[System]: The discussion on \"{self.topic}\" begins now. Please share your view."
                )],
            ))

        # Gemini also requires strict alternation between user/model.
        # Merge consecutive same-role messages.
        contents = self._merge_consecutive(contents)
        return contents

    @staticmethod
    def _merge_consecutive(contents: list) -> list:
        """Merge consecutive messages of the same role."""
        if not contents:
            return contents
        merged = [contents[0]]
        for c in contents[1:]:
            if c.role == merged[-1].role:
                old_text = merged[-1].parts[0].text
                new_text = c.parts[0].text
                merged[-1] = types.Content(
                    role=c.role,
                    parts=[types.Part.from_text(text=f"{old_text}\n\n{new_text}")],
                )
            else:
                merged.append(c)
        return merged


def get_persona_response(conversation: Conversation, persona_id: str, max_retries: int = 3) -> str:
    """
    Generate one reply from the specified persona, based on the current history.
    Includes retry logic for Gemini free-tier rate limits (429) and busy servers (503).
    """
    persona = get_persona(persona_id)
    contents = conversation.format_for_persona(persona_id)

    # Inject the topic into the system prompt
    system_prompt = persona["system_prompt"]
    if conversation.topic:
        system_prompt += f"\n\n[The Topic of This Discussion]\n{conversation.topic}"

    config = types.GenerateContentConfig(
        system_instruction=system_prompt,
        max_output_tokens=1500,
        temperature=0.9,  # Slightly high temperature so personas feel more distinct
    )

    # Retry on transient errors: rate limit (429) or service unavailable (503)
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=contents,
                config=config,
            )
            reply = response.text.strip() if response.text else ""
            if not reply:
                # Occasionally Gemini returns an empty response (safety filter, etc.)
                raise RuntimeError("Model returned an empty response (possibly blocked by safety filter)")
            conversation.add_message(persona_id, persona["name"], reply)
            return reply
        except Exception as e:
            err_str = str(e)
            is_retriable = (
                "429" in err_str
                or "503" in err_str
                or "RESOURCE_EXHAUSTED" in err_str
                or "UNAVAILABLE" in err_str
                or "rate" in err_str.lower()
                or "high demand" in err_str.lower()
            )
            if is_retriable:
                wait_time = 2 ** attempt * 5  # 5s, 10s, 20s
                if attempt < max_retries - 1:
                    print(f"   [Retrying] Server busy or rate-limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue
            raise

    raise RuntimeError(
        f"Failed after {max_retries} retries. Google's service may be busy - please try again later."
    )