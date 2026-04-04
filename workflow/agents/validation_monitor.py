import asyncio
import json
import os
from datetime import datetime
from typing import Optional

from langchain_core.runnables import RunnableConfig
from workflow.state import WorkflowState
from workflow.storage import file_lock, load_instructions

async def validation_monitor_node(
    state: WorkflowState,
    config: Optional[RunnableConfig] = None,
):
    """
    Continuously monitors stored instructions and logs how many require user validation.
    
    This background task repeatedly (every 5 seconds) acquires the shared file lock, counts records whose "status" is "Requires user validation", and prints a UTC timestamped message with the count. The `state` and optional `config` parameters are accepted for integration but are not used by this monitor.
    """
    while True:
        async with file_lock:

            instructions = await load_instructions()

            count = sum(
                1
                for r in instructions
                if r.get("status") == "Requires user validation"
            )

        print(
            f"[{datetime.utcnow().isoformat()}] "
            f"Records requiring validation: {count}"
        )

        await asyncio.sleep(5)  # Check every 5 seconds