import os
import json
import uuid
from datetime import datetime
from typing import Optional

from langchain_core.runnables import RunnableConfig

from workflow.state import WorkflowState
from workflow.storage import file_lock, load_instructions, save_instructions

def clean_text(text: str) -> str:
    """
    Normalize whitespace in a string.
    
    Strips leading and trailing whitespace and collapses any runs of internal whitespace
    (including tabs and newlines) into single space characters.
    
    Parameters:
        text (str): The input string to normalize.
    
    Returns:
        str: The cleaned string with no leading/trailing whitespace and single spaces between tokens.
    """
    return " ".join(text.strip().split())


async def instruction_editor_node(
    state: WorkflowState,
    config: Optional[RunnableConfig] = None,
):
    """
    Append a cleaned instruction to the persistent instructions store and return metadata about the operation.
    
    Parameters:
        state (WorkflowState): Execution state containing at least a "raw_text" entry; may include "user_id" to associate the instruction with an existing user (a new UUID is generated if absent).
    
    Returns:
        dict: A mapping with the following keys:
            - "user_id": the user identifier associated with the instruction.
            - "raw_text": the original text supplied in `state["raw_text"]`.
            - "cleaned_text": the normalized text after whitespace normalization.
            - "instruction_record": the persisted instruction record containing "user_id", "timestamp" (ISO 8601 UTC), "text" (cleaned_text), and "status" set to "new".
    """

    user_id = state.get("user_id") or str(uuid.uuid4())
    raw_text = state["raw_text"]
    cleaned = clean_text(raw_text)

    record = {
        "user_id": user_id,
        "timestamp": datetime.utcnow().isoformat(),
        "text": cleaned,
        "status": "new",
    }

    # ---------------------------
    # Critical Section (Locked)
    # ---------------------------
    async with file_lock:

        instructions = await load_instructions()

        instructions.append(record)

        await save_instructions(instructions)

    # ---------------------------

    return {
        "user_id": user_id,
        "raw_text": raw_text,
        "cleaned_text": cleaned,
        "instruction_record": record,
    }