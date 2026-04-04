*********************** Coding under Lightning ai **********************************************

Dependencies:
--------------
pip install arize-phoenix opentelemetry-sdk opentelemetry-exporter-otlp openinference-instrumentation-langchain
pip install -U langchain-core langgraph
pip install groq

Principle :
-------------
4 agents for parsing and executing user instruction
use Opentelemetry to trace the workflow and monitor the agents with Arize Phoenix

Agent workflow:
----------------
- Agent 1 : Instruction Editor
Prompt the user for instruction and save it into a json file
json details: user id, timestamp, text, status

- Agent 2 : Instruction scanner
Scan the file Instruction.json for instruction and update new instruction flag

- Agent 3 : Instruction parsing
Load the instruction and identify the nature of the instruction with LLM

- Agent 4 : Instruction execution - oversight the instruction
Ask the user for permission if action related to payment




Agent tracing and workflow
---------------------------
python -m phoenix.server.main serve
Open : https://6006-01khzfs7mzxsfdya9sqzk90hsw.cloudspaces.litng.ai/

Architecture
--------------------------
Editor (async loop)
        ↓
JSON / DB
        ↓
Scanner (async loop)
        ↓
graph.invoke()
        ↓
Planner
        ↓
Executor
        ↓
Status Updater