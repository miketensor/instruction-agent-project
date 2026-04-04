import json
import os
from asyncio import Lock

DATA_PATH = "data_in/instruction.json"

# ✅ One global lock for the entire app
file_lock = Lock()


async def load_instructions():
    if not os.path.exists(DATA_PATH):
        return []

    try:
        with open(DATA_PATH, "r") as f:
            content = f.read().strip()

            # If file empty → return empty list
            if not content:
                return []

            return json.loads(content)

    except json.JSONDecodeError:
        # File corrupted → reset it safely
        print("⚠ JSON corrupted. Resetting file.")
        with open(DATA_PATH, "w") as f:
            json.dump([], f)

        return []


async def save_instructions(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)