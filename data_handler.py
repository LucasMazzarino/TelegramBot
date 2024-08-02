import json
import os

CONVERSATIONS_FILE = 'conversations.json'


def load_conversations():
    if os.path.exists(CONVERSATIONS_FILE):
        with open(CONVERSATIONS_FILE, 'r') as f:
            return json.load(f)
    return {}


def save_conversations(conversations):
    with open(CONVERSATIONS_FILE, 'w') as f:
        json.dump(conversations, f)


def store_user_message(user_id: str, message: str) -> None:
    conversations = load_conversations()
    if user_id not in conversations:
        conversations[user_id] = []
    conversations[user_id].append(message)
    save_conversations(conversations)


def get_user_conversation(user_id: str):
    conversations = load_conversations()
    return conversations.get(user_id, [])