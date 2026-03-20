import json
import os

CHAT_DIR = "bookchunker/chats"


def load_all_chats():

    chats = []

    if not os.path.exists(CHAT_DIR):
        return chats

    for f in os.listdir(CHAT_DIR):
        if f.endswith(".json"):

            with open(os.path.join(CHAT_DIR, f)) as file:
                chats.append(json.load(file))

    return chats