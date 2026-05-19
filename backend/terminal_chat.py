"""
Multi-Persona AI Chatroom (Terminal version)
Use this to validate the core logic before building the web UI.

Usage:
    python terminal_chat.py

Commands:
    Type 1/2/3 to let the corresponding persona speak
    Type 'a' to let all personas speak one round each
    Type 'q' to quit
    Type anything else to chime in as the user
"""

from chat_engine import Conversation, get_persona_response
from personas import PERSONAS


def print_message(speaker: str, avatar: str, content: str):
    """Pretty-print a single message."""
    print(f"\n{avatar}  \033[1m{speaker}\033[0m")
    print(f"   {content}")
    print()


def main():
    print("=" * 60)
    print("🎭 Multi-Persona AI Chatroom (Terminal)")
    print("=" * 60)

    # Show the available personas
    print("\nAvailable personas:")
    persona_ids = list(PERSONAS.keys())
    for i, pid in enumerate(persona_ids, 1):
        p = PERSONAS[pid]
        print(f"  {i}. {p['avatar']} {p['name']}")

    # Ask for a topic
    topic = input("\nEnter a discussion topic: ").strip()
    if not topic:
        topic = "What is truth?"
        print(f"(Using default topic: {topic})")

    conversation = Conversation(topic=topic)
    print(f"\n📌 Topic: {topic}")
    print("=" * 60)
    print("\nCommands:  1/2/3 = pick a persona to speak  |  a = all speak one round  |  q = quit")
    print("Any other text = you chime in\n")

    while True:
        user_input = input("\n👤 You > ").strip()

        if not user_input:
            continue

        if user_input.lower() == "q":
            print("\nGoodbye!")
            break

        if user_input.lower() == "a":
            # Each persona speaks once, in order
            for pid in persona_ids:
                p = PERSONAS[pid]
                print(f"\n💭 {p['name']} is thinking...")
                try:
                    reply = get_persona_response(conversation, pid)
                    print_message(p["name"], p["avatar"], reply)
                except Exception as e:
                    print(f"❌ Error: {e}")
            continue

        # Numeric command: speak as that persona
        if user_input.isdigit():
            idx = int(user_input) - 1
            if 0 <= idx < len(persona_ids):
                pid = persona_ids[idx]
                p = PERSONAS[pid]
                print(f"\n💭 {p['name']} is thinking...")
                try:
                    reply = get_persona_response(conversation, pid)
                    print_message(p["name"], p["avatar"], reply)
                except Exception as e:
                    print(f"❌ Error: {e}")
                continue
            else:
                print(f"❌ No persona #{user_input}")
                continue

        # Otherwise, treat the input as a user message
        conversation.add_user_message(user_input)
        print(f"   (Recorded. Type 1/2/3 to have a persona respond, or 'a' for all)")


if __name__ == "__main__":
    main()