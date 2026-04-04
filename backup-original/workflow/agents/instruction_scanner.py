import json
import os
from typing import Optional

from datetime import datetime
from opentelemetry import trace
from langchain_core.runnables import RunnableConfig

from workflow.state import WorkflowState
from workflow.agents.instruction_classifier import classify_instruction_with_llm
from workflow.storage import file_lock, load_instructions, save_instructions

tracer = trace.get_tracer(__name__)

# ----------------------------
# Agent 2 Node
# ----------------------------
async def instruction_scanner_node(
    state: WorkflowState,
    config: Optional[RunnableConfig] = None,
):
    """
    Select the first persisted instruction with status "new", update its status according to an LLM classification, persist the change, and return the selected instruction with extracted metadata.
    
    This function acquires a file lock, scans stored instructions to find the first record whose `status` is `"new"`, updates that record's status and processing timestamp, classifies the instruction text to decide whether it requires user validation or can be executed, and saves the updated instruction list. It also records input and output into the active tracing span.
    
    Parameters:
        state (WorkflowState): Current workflow state provided to the node.
    
    Returns:
        dict: If an instruction was selected, returns a dict with:
            - "scanned_instruction": the updated instruction record (dict)
            - "user_id": the selected instruction's `user_id`
            - "raw_text": the selected instruction's `text`
        Otherwise returns:
            - {"scanned_instruction": None}
    """
    with tracer.start_as_current_span("instruction_scanner") as span:

        selected_instruction: Optional[dict] = None
        
        span.set_attribute(
            "input",
            json.dumps(state)
        )

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
                            f"**** NEW INSTRUCTION REQUIRING USER VALIDATION: {record.get("text")} *****"
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
            span.set_attribute(
                    "output",
                    json.dumps(selected_instruction)
                )
            
            return {
                "scanned_instruction": selected_instruction,
                "user_id": selected_instruction["user_id"],
                "raw_text": selected_instruction["text"],
            }

        span.set_attribute(
                "output",
                ""
            )
    
        return {
            "scanned_instruction": None
        }