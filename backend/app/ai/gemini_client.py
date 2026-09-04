"""
Gemini Client Wrapper.
Uses the official google-genai SDK for intelligent Hinglish voice NLU and recovery conversation.
Gracefully handles missing keys, timeouts, or network failures.
"""

import os
import json
from typing import Optional, Dict, Any
from app.config import settings

client = None
if settings.GEMINI_API_KEY:
    try:
        from google import genai
        client = genai.Client(api_key=settings.GEMINI_API_KEY)
    except Exception as e:
        print(f"[Gemini Client Warning] Could not initialize google-genai SDK: {e}")
        client = None

def query_gemini_json(prompt: str, system_instruction: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """Calls Gemini with schema / JSON format expectation."""
    if not client:
        return None
    
    try:
        response = client.models.generate_content(
            model=settings.GEMINI_MODEL,
            contents=prompt,
            config={
                "system_instruction": system_instruction or "You are an AI Revenue Recovery assistant for Razorpay merchants.",
                "response_mime_type": "application/json",
                "temperature": 0.1
            }
        )
        if response and response.text:
            return json.loads(response.text)
    except Exception as e:
        print(f"[Gemini Query Error] {e}")
        return None
    return None
