import os
import json
import uuid
from datetime import datetime
from typing import Optional

from langchain_core.runnables import RunnableConfig

from workflow.state import WorkflowState
from workflow.storage import file_lock, load_instructions, save_instructions

def clean_text(text: str) -> str:
    """Basic cleansing logic."""
    return " ".join(text.strip().split())


async def instruction_editor_node(
    state: WorkflowState,
    config: Optional[RunnableConfig] = None,
):
    """
    Writes a new instruction into instruction.json safely using a shared async lock.
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