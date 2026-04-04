import json
import os
from typing import Optional

from datetime import datetime
from langchain_core.runnables import RunnableConfig

from workflow.state import WorkflowState
from workflow.agents.instruction_classifier import classify_instruction_with_llm
from workflow.storage import file_lock, load_instructions, save_instructions

# ----------------------------
# Agent 2 Node
# ----------------------------
async def instruction_scanner_node(
    state: WorkflowState,
    config: Optional[RunnableConfig] = None,
):
    selected_instruction: Optional[dict] = None

    # -----------------------
    # Critical Section
    # -----------------------
    async with file_lock:

        instructions = await load_instructions()

        for record in instructions:
            if record.get("status") == "new":
                record["status"] = "processing"
                record["processing_timestamp"] = datetime.utcnow().isoformat()
                
                result_classifier = await classify_instruction_with_llm(record.get("text"))
                if result_classifier.get("is_payment") == True:
                    print(
                        f"[{datetime.utcnow().isoformat()}] "
                        f"**** NEW INSTRUCTION REQUIRING USER VALIDATION: {record.get('text')} *****"
                    )
                    record["status"] = "Requires user validation"
                else:
                    record["status"] = "To be executed"

                selected_instruction = record
                break

        if selected_instruction:
            await save_instructions(instructions)
    # -----------------------
            
    if selected_instruction:
        
        return {
            "scanned_instruction": selected_instruction,
            "user_id": selected_instruction["user_id"],
            "raw_text": selected_instruction["text"],
        }

    
    return {
        "scanned_instruction": None
    }