import os
import sys
import json
from opentelemetry import trace
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY not set in Lightning Secrets")

client = Groq(api_key=api_key)
MODEL_NAME = "llama-3.1-8b-instant"  # Groq supported model

tracer = trace.get_tracer(__name__)

async def classify_instruction_with_llm(text: str) -> dict:
    """
    Classifies whether the given instruction pertains to payments or other financial transactions.
    
    Parameters:
        text (str): Instruction text to classify.
    
    Returns:
        dict: A dictionary with keys:
            - "is_payment": `true` if the instruction relates to payment, transfer, billing, invoice, subscription, or other financial transaction, `false` otherwise.
            - "reason": short string explaining the classification or an error reason when parsing fails.
    """
    with tracer.start_as_current_span("instruction_classifier"):
        prompt = f"""
    You are a classifier.

    Determine whether the following instruction is related to payment,
    money transfer, billing, invoice, subscription, or financial transaction.

    Instruction:
    {text}

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
                return json.loads(content)
            else:
                return {
                    "is_payment": False,
                    "reason": "Invalid JSON from model"
                }    
        except json.JSONDecodeError:
            return {
                "is_payment": False,
                "reason": "Invalid JSON from model"
            }