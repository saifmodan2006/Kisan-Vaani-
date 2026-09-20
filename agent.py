"""
Kisan Vaani - Agent Module with Gemini Native Function Calling.
"""

import os
import sys
import warnings
from typing import Optional

# Suppress deprecation and transport warnings for clean execution
warnings.filterwarnings("ignore")

from dotenv import load_dotenv
import google.generativeai as genai

from tools import get_mandi_price, check_scheme_eligibility

# Load environment variables from .env if present
load_dotenv()

SYSTEM_INSTRUCTION = """
You are "Kisan Vaani" (किसान वाणी), an empathetic, respectful, and reliable AI assistant dedicated to empowering Indian farmers.

Your two core capabilities are:
1. Mandi Prices: Looking up commodity market prices across APMC mandis and districts using the get_mandi_price tool.
2. Scheme Eligibility: Assessing qualifications and benefits for government agricultural schemes (PM-KISAN, PMFBY crop insurance, SMAM machinery subsidy) using the check_scheme_eligibility tool.

Important Behavior Rules:
- Intent Detection & Clarification:
  a) If asking about mandi prices: Ensure you know BOTH the crop name AND the district. If either is missing from the query, DO NOT guess or hallucinate; warmly ask a clarifying follow-up question (e.g., "Which district's mandi price would you like to check?").
  b) If asking about government schemes: Ensure you know BOTH the land size in acres AND whether they are a land-owning farmer or a tenant farmer. If either detail is missing, warmly ask for it before calling the tool.
- Tool Calling: When calling a tool, do not output intermediate "please wait" or filler text. Call the tool directly and formulate your complete response once the data is retrieved.
- Language Matching: Strictly match the user's language:
  - If the user writes in English, answer in friendly, polite, simple English.
  - If the user writes in Hindi or Hinglish, answer in warm Hindi (using Devanagari script).
- Presentation: NEVER return raw JSON, dictionary dumps, or technical schemas to the user. Synthesize tool results into clean, conversational summaries with bullet points and rupee symbols (₹).
- Tone: Warm, respectful, rural-friendly, and encouraging.
"""

# Primary and fallback models for high availability and quota resilience
DEFAULT_MODEL = "gemini-3.6-flash"
FALLBACK_MODELS = ["gemini-3.6-flash", "gemini-3.5-flash", "gemini-flash-latest", "gemini-flash-lite-latest"]


def get_api_key() -> Optional[str]:
    """Retrieve the Gemini API key from environment variables."""
    return os.environ.get("GEMINI_API_KEY")


def configure_gemini(api_key: Optional[str] = None) -> None:
    """Configure the Gemini SDK with the API key."""
    key = api_key or get_api_key()
    if not key:
        raise ValueError(
            "GEMINI_API_KEY not found. Please set GEMINI_API_KEY in your environment or in a .env file."
        )
    genai.configure(api_key=key)


def create_agent(model_name: str = DEFAULT_MODEL) -> genai.GenerativeModel:
    """
    Initialize and return the GenerativeModel configured with tools and system instruction.
    """
    configure_gemini()

    # Tools are registered as callable functions; SDK handles schema reflection
    model = genai.GenerativeModel(
        model_name=model_name,
        tools=[get_mandi_price, check_scheme_eligibility],
        system_instruction=SYSTEM_INSTRUCTION.strip(),
    )
    return model


def start_chat_session(model_name: str = DEFAULT_MODEL):
    """
    Start a new multi-turn chat session with automatic function calling enabled.
    """
    model = create_agent(model_name=model_name)
    chat = model.start_chat(enable_automatic_function_calling=True)
    chat._current_model_name = model_name
    return chat


def send_message(chat_session, message: str) -> str:
    """
    Send a message to the chat session and retrieve the final synthesized response text.
    Includes automatic failover to fallback models if quota (429) or rate limits are reached.
    """
    try:
        response = chat_session.send_message(message)
        if chat_session.history and chat_session.history[-1].role == "model":
            last_parts = chat_session.history[-1].parts
            text_parts = [p.text for p in last_parts if p.text]
            if text_parts:
                return "".join(text_parts).strip()
        return response.text.strip()
    except Exception as e:
        err_str = str(e).lower()
        if "429" in err_str or "quota" in err_str or "not_found" in err_str:
            # Attempt failover with alternative models
            current = getattr(chat_session, "_current_model_name", DEFAULT_MODEL)
            for fallback in FALLBACK_MODELS:
                if fallback != current:
                    try:
                        print(f"Quota issue with {current}, falling back to {fallback}...")
                        new_chat = start_chat_session(model_name=fallback)
                        res = new_chat.send_message(message)
                        return res.text.strip()
                    except Exception:
                        continue
        raise e


