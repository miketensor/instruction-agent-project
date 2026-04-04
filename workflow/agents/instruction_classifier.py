import os
import sys
import json
import re
from opentelemetry import trace
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not set in Lightning Secrets")

client = Groq(api_key=api_key)
MODEL_NAME = "llama-3.1-8b-instant"  # Groq supported model

# tracer = trace.get_tracer(__name__)

def sanitize_input(text: str) -> str:
    """Sanitize user input to prevent prompt injection."""
    # Remove or escape potentially dangerous characters
    text = text.strip()
    # Remove newlines and tabs that could break prompt structure
    text = re.sub(r'[\n\r\t]', ' ', text)
    # Limit length to prevent overly long inputs
    return text[:1000]  # Reasonable limit for instruction text

async def classify_instruction_with_llm(text: str) -> dict:
    # with tracer.start_as_current_span("instruction_classifier"):
    # Sanitize input to prevent prompt injection
    sanitized_text = sanitize_input(text)
    
    prompt = f"""
You are a classifier.

Determine whether the following instruction is related to payment,
money transfer, billing, invoice, subscription, or financial transaction.

Instruction:
{sanitized_text}

Respond strictly in JSON:
{{
"is_payment": true or false,
"reason": "short explanation"
}}
"""
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0,
    )

    content = response.choices[0].message.content

    try:
        if content is not None:
            result = json.loads(content)
            # Validate response structure
            if not isinstance(result, dict) or 'is_payment' not in result or 'reason' not in result:
                raise ValueError("Invalid response structure")
            return result
        else:
            return {
                "is_payment": False,
                "reason": "Invalid JSON from model"
            }    
    except (json.JSONDecodeError, ValueError):
        return {
            "is_payment": False,
            "reason": "Invalid JSON from model"
        }