from typing import TypedDict

# required entries
class InstructionInput(TypedDict):
    user_id: str
    raw_text: str

# optional entries
class WorkflowState(InstructionInput, total=False):
    cleaned_text: str
    instruction_record: dict
    scanned_instruction: dict
    plan: dict
    execution_result: dict
    final_status: str