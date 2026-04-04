from typing import TypedDict
from langgraph.graph import StateGraph, END
from workflow.agents.instruction_editor import instruction_editor_node
from workflow.agents.instruction_scanner import instruction_scanner_node
from workflow.agents.validation_monitor import validation_monitor_node

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from openinference.instrumentation.langchain import LangChainInstrumentor

import asyncio
from workflow.state import WorkflowState

# --- 1. OPENTELEMETRY & PHOENIX SETUP ---
endpoint = "http://localhost:6006/v1/traces"
provider = TracerProvider()
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint)))
trace.set_tracer_provider(provider)
tracer = trace.get_tracer(__name__)

LangChainInstrumentor().instrument()

shutdown_event = asyncio.Event()

# ---------------------------
# Agent 1: Instruction Editor
# ---------------------------
async def instruction_editor_loop():
    """
    Continuously prompts the user for instructions and forwards each input to the instruction editor node until shutdown is requested.
    
    Prompts the user with "Type 'STOP' to shut down the system else Enter instruction:". If the user enters "STOP" (case-insensitive, whitespace ignored), the function sets the module-level shutdown_event and exits the loop. For any other input, it constructs a WorkflowState with "user_id": "user_001" and "raw_text" set to the input, then awaits instruction_editor_node(state).
    
    On cancellation, prints "Editor loop cancelled" and re-raises asyncio.CancelledError.
    """
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
    """
    Continuously polls the instruction scanner node and prints any discovered instruction text.
    
    This loop repeatedly calls the module-level `instruction_scanner_node` with an empty workflow state, prints `scanned_instruction["text"]` when a scanned instruction is returned, and sleeps between iterations. The loop runs until the module-level `shutdown_event` is set.
    """
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
    """
    Periodically invokes the validation monitor node until the global shutdown_event is set.
    
    On each iteration it constructs a WorkflowState with "user_id" set to "user_001" and an empty "raw_text", passes it to `validation_monitor_node`, then waits five seconds before repeating.
    """
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
    
    """
    Start three concurrent loops (instruction editor, instruction scanner, validation monitor), wait for the module-level shutdown_event to be set, then cancel those loops and wait for their termination.
    
    Prints a shutdown announcement before cancelling tasks and a final confirmation after all tasks complete.
    """
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