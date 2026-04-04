from typing import TypedDict
from langgraph.graph import StateGraph, END
from workflow.agents.instruction_editor import instruction_editor_node
from workflow.agents.instruction_scanner import instruction_scanner_node
from workflow.agents.validation_monitor import validation_monitor_node

import asyncio
from workflow.state import WorkflowState

shutdown_event = asyncio.Event()

# ---------------------------
# Agent 1: Instruction Editor
# ---------------------------
async def instruction_editor_loop():
    try:
        while not shutdown_event.is_set():
            user_input = await asyncio.to_thread(input, "Type 'STOP' to shut down the system else Enter instruction: ")

            if user_input.strip().lower() == "stop":
                print("Shutting down system...")
                shutdown_event.set()
                break

            state: WorkflowState = {
                "user_id": "user_001",
                "raw_text": user_input,
            }

            await instruction_editor_node(state)

    except asyncio.CancelledError:
        print("Editor loop cancelled")
        raise

# ---------------------------
# Agent 2: Instruction Scanner
# ---------------------------
async def instruction_scanner_loop():
    while not shutdown_event.is_set():
        state: WorkflowState = {
            "user_id": "user_001",
            "raw_text": "",
        }

        result = await instruction_scanner_node(state)
        scanned = result.get("scanned_instruction")

        if scanned is not None:
            print("Processing instruction:")
            print(scanned["text"])

        await asyncio.sleep(5)
        
# ---------------------------
# Agent 3: Validation monitor
# ---------------------------
async def validation_monitor_loop():
    while not shutdown_event.is_set():
        state: WorkflowState = {
            "user_id": "user_001",
            "raw_text": "",
        }

        result = await validation_monitor_node(state)

        await asyncio.sleep(5)

# ---------------------------
# Main Concurrent Runtime
# ---------------------------
async def main():
    
    tasks = [
        asyncio.create_task(instruction_editor_loop()),
        asyncio.create_task(instruction_scanner_loop()),
        asyncio.create_task(validation_monitor_loop()),
    ]

    # Wait until shutdown_event is set (i.e. user typed STOP)
    await shutdown_event.wait()

    print("Shutdown signal received, cancelling all tasks...")
    
    for task in tasks:
        task.cancel()

    await asyncio.gather(*tasks, return_exceptions=True)

    print("System fully stopped.")

if __name__ == "__main__":
    asyncio.run(main())