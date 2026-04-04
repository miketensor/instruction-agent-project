import json
import os
from asyncio import Lock
from jsonschema import validate, ValidationError

DATA_PATH = "data_in/instruction.json"

# JSON Schema for instruction records
INSTRUCTION_SCHEMA = {
    "type": "object",
    "properties": {
        "user_id": {"type": "string"},
        "timestamp": {"type": "string"},
        "text": {"type": "string"},
        "status": {"type": "string"},
        "processing_timestamp": {"type": "string"}
    },
    "required": ["user_id", "timestamp", "text", "status"]
}

INSTRUCTIONS_SCHEMA = {
    "type": "array",
    "items": INSTRUCTION_SCHEMA
}

# ✅ One global lock for the entire app
file_lock = Lock()


async def load_instructions():
    """
    Load and validate instructions from the persistent JSON file.
    
    If the storage file does not exist or is empty, returns an empty list. If the file contains invalid JSON or fails schema validation, the file is reset to an empty JSON array and an empty list is returned.
    
    Returns:
        list: Instruction objects read from the file; empty list if the file is missing, empty, corrupted, or invalid.
    """
    if not os.path.exists(DATA_PATH):
        return []

    try:
        with open(DATA_PATH, "r") as f:
            content = f.read().strip()

            # If file empty → return empty list
            if not content:
                return []

            data = json.loads(content)
            
            # Validate JSON structure
            validate(instance=data, schema=INSTRUCTIONS_SCHEMA)
            
            return data

    except (json.JSONDecodeError, ValidationError) as e:
        # File corrupted or invalid schema → reset it safely
        print(f"⚠ JSON corrupted or invalid: {e}. Resetting file.")
        with open(DATA_PATH, "w") as f:
            json.dump([], f)

        return []


async def save_instructions(data):
    with open(DATA_PATH, "w") as f:
        json.dump(data, f, indent=2)