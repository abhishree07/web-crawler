import json
import os

STATE_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "seen_jobs.json")


def load_seen_ids():
    if not os.path.exists(STATE_FILE):
        return set()
    with open(STATE_FILE, "r") as f:
        return set(json.load(f))


def save_seen_ids(ids):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(sorted(ids), f, indent=2)
