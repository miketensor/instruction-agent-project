import os
import json
import uuid
from datetime import datetime
from typing import Optional

from opentelemetry import trace
from langchain_core.runnables import RunnableConfig

from workflow.state import WorkflowState
from workflow.storage import file_lock, load_instructions, save_instructions

tracer = trace.get_tracer(__name__)

def clean_text(text: str) -> str:
    """
    Normalize whitespace in a text string.
    
    Parameters:
        text (str): The input string to normalize.
    
    Returns:
        str: The input with leading and trailing whitespace removed and all internal runs of whitespace collapsed into single spaces.
    """
    return " ".join(text.strip().split())


async def instruction_editor_node(
    state: WorkflowState,
    config: Optional[RunnableConfig] = None,
):
    """
    Create, persist, and return a cleaned instruction record derived from the provided workflow state.
    
    The function extracts `raw_text` (and optionally `user_id`) from `state`, normalizes the text, constructs an instruction record with a UTC ISO-8601 timestamp and status `"new"`, persists that record to the shared instruction store, and returns metadata about the created record.
    
    Parameters:
        state (WorkflowState): Workflow state containing at least the key `"raw_text"`. If `"user_id"` is present it will be used; otherwise a new UUID will be generated.
    
    Returns:
        dict: A mapping with the following keys:
            - `user_id` (str): The user identifier associated with the instruction.
            - `raw_text` (str): The original text from `state`.
            - `cleaned_text` (str): The normalized text after whitespace collapsing.
            - `instruction_record` (dict): The persisted instruction record containing `user_id`, `timestamp` (UTC ISO-8601 string), `text` (cleaned), and `status` (`"new"`).
    """

    with tracer.start_as_current_span("instruction_editor") as span:
        # Log Input
        span.set_attribute(
            "input",
            json.dumps(state)
        )

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
        span.set_attribute(
                    "output",
                    json.dumps(record)
                )

        return {
            "user_id": user_id,
            "raw_text": raw_text,
            "cleaned_text": cleaned,
            "instruction_record": record,
        }