import json
import os

SEEN_FILE = "seen_posts.json"


def load_seen_posts():
    if not os.path.exists(SEEN_FILE):
        return set()

    with open(SEEN_FILE, "r", encoding="utf-8") as file:
        return set(json.load(file))


def save_seen_posts(seen_posts):
    with open(SEEN_FILE, "w", encoding="utf-8") as file:
        json.dump(list(seen_posts), file, ensure_ascii=False, indent=2)
        
def is_first_run():
    return not os.path.exists(SEEN_FILE)