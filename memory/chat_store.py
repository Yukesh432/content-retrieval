import json
import os
import uuid
from datetime import datetime

CHAT_DIR = "bookchunker/chats"


def save_chat(history):

    os.makedirs(CHAT_DIR, exist_ok=True)

    chat_id = str(uuid.uuid4())

    data = {
        "chat_id": chat_id,
        "timestamp": datetime.utcnow().isoformat(),
        "messages": history,
    }

    path = os.path.join(CHAT_DIR, f"{chat_id}.json")

    with open(path, "w") as f:
        json.dump(data, f, indent=2)

    return path