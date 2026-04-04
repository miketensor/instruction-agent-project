import asyncio
import json
import os
from datetime import datetime
from typing import Optional

from opentelemetry import trace
from langchain_core.runnables import RunnableConfig
from workflow.state import WorkflowState
from workflow.storage import file_lock, load_instructions

tracer = trace.get_tracer(__name__)

async def validation_monitor_node(
    state: WorkflowState,
    config: Optional[RunnableConfig] = None,
):
    """
    Background agent that continuously monitors
    how many instructions require user validation.
    """
    with tracer.start_as_current_span("validation_monitor") as span:
        # Log Input
        span.set_attribute(
            "input",
            "scan the instruction file"
        )

    while True:
        async with file_lock:

            instructions = await load_instructions()

            count = sum(
                1
                for r in instructions
                if r.get("status") == "Requires user validation"
            )

        # Trace it
        with tracer.start_as_current_span("validation_monitor") as span:
            span.set_attribute("validation_count", count)

        print(
            f"[{datetime.utcnow().isoformat()}] "
            f"Records requiring validation: {count}"
        )

        await asyncio.sleep(5)  # Check every 5 seconds