import json
import os
from asyncio import Lock

DATA_PATH = "data_in/instruction.json"

# ✅ One global lock for the entire app
file_lock = Lock()


async def load_instructions():
    """
    Load stored instructions from DATA_PATH, returning an empty list if the file is missing, empty, or contains invalid JSON.
    
    If the file does not exist or contains only whitespace, this function returns an empty list. If the file contains invalid JSON, it prints a warning, overwrites the file with an empty JSON array, and returns an empty list. Otherwise, it returns the parsed JSON value.
    
    Returns:
        list | Any: Parsed JSON content from the file (typically a list of instructions); `[]` when the file is missing, empty, or corrupted.
    """
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
    """
    Write the given object to DATA_PATH as pretty-printed JSON, overwriting any existing file contents.
    
    Parameters:
        data: A JSON-serializable Python object (for example, a list or dict) to be persisted.
    """
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)