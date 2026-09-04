"""
Voice NLU & Intent Engine.
Supports Hinglish, Devanagari, and English speech-to-text transcripts.
Extracts recovery intent, extracts promise-to-pay dates, and provides synthesized voice audio/text responses.
Combines Gemini generative intelligence with a 100% deterministic regex fallback.
"""

import re
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
from app.ai.gemini_client import query_gemini_json

# Core Intent Types
INTENTS = {
    "PAY_NOW",
    "PAY_LATER",
    "PAYMENT_METHOD_PROBLEM",
    "CANNOT_PAY",
    "REFUSE",
    "HUMAN_ESCALATION",
    "UNCLEAR"
}

# Regex patterns for deterministic fallback
FALLBACK_PATTERNS = {
    "REFUSE": [
        r"\b(nahi|nahin|cancel|don't|dont|band|mat|refuse|stop|nahi chahiye|nahi karna|kisi aur se leliya)\b",
        r"(नहीं|मत|कैंसल|बंद|नहीं चाहिए)"
    ],
    "PAY_NOW": [
        r"\b(abhi|now|link|haan|yes|pay kar|bhejo|bhej do|karna hai|try|dobara|ready|kardunga abhi)\b",
        r"(अभी|हाँ|लिंक|पे|भेजो|कर दो|तैयार)"
    ],
    "PAY_LATER": [
        r"\b(later|kal|parso|parson|baad mein|salary|friday|monday|tuesday|tarikh|din baad|thoda time|next week)\b",
        r"(बाद में|कल|परसों|सैलरी|तारीख|दिन बाद|अगले हफ्ते)"
    ],
    "PAYMENT_METHOD_PROBLEM": [
        r"\b(card reject|upi fail|bank server|decline|error|limit|doosra|dusra|change payment|google pay|phonepe)\b",
        r"(कार्ड|बैंक|लिमिट|दूसरा|फेल|दिक्कत)"
    ],
    "CANNOT_PAY": [
        r"\b(paise nahi|paisa nahi|no money|insufficient|broke|afford|kangal)\b",
        r"(पैसे नहीं|रुपये नहीं|कंगाल)"
    ],
    "HUMAN_ESCALATION": [
        r"\b(agent|human|manager|executive|support|customer care|baat karvao|baat karni)\b",
        r"(एजेंट|मैनेजर|कस्टमर केयर|बात करवाओ)"
    ]
}

def deterministic_classify(text: str) -> Dict[str, Any]:
    """Pure deterministic regex intent classifier (Negation & Refusal evaluated first!)."""
    lower = text.lower().strip()
    
    # 1. Check REFUSE first
    for pat in FALLBACK_PATTERNS["REFUSE"]:
        if re.search(pat, lower):
            return {
                "intent": "REFUSE",
                "confidence": 0.95,
                "classifier": "deterministic_keyword_negation_first"
            }
            
    # 2. Check HUMAN_ESCALATION
    for pat in FALLBACK_PATTERNS["HUMAN_ESCALATION"]:
        if re.search(pat, lower):
            return {
                "intent": "HUMAN_ESCALATION",
                "confidence": 0.92,
                "classifier": "deterministic_keyword"
            }
            
    # 3. Check PAYMENT_METHOD_PROBLEM
    for pat in FALLBACK_PATTERNS["PAYMENT_METHOD_PROBLEM"]:
        if re.search(pat, lower):
            return {
                "intent": "PAYMENT_METHOD_PROBLEM",
                "confidence": 0.90,
                "classifier": "deterministic_keyword"
            }

    # 4. Check PAY_LATER
    for pat in FALLBACK_PATTERNS["PAY_LATER"]:
        if re.search(pat, lower):
            return {
                "intent": "PAY_LATER",
                "confidence": 0.92,
                "classifier": "deterministic_keyword"
            }

    # 5. Check CANNOT_PAY
    for pat in FALLBACK_PATTERNS["CANNOT_PAY"]:
        if re.search(pat, lower):
            return {
                "intent": "CANNOT_PAY",
                "confidence": 0.88,
                "classifier": "deterministic_keyword"
            }

    # 6. Check PAY_NOW
    for pat in FALLBACK_PATTERNS["PAY_NOW"]:
        if re.search(pat, lower):
            return {
                "intent": "PAY_NOW",
                "confidence": 0.94,
                "classifier": "deterministic_keyword"
            }

    return {
        "intent": "UNCLEAR",
        "confidence": 0.40,
        "classifier": "deterministic_fallback"
    }

def extract_promise_offset_days(text: str) -> int:
    """Extracts promise date offset in days from transcript."""
    lower = text.lower()
    if "kal" in lower or "tomorrow" in lower:
        return 1
    if "parso" in lower or "parson" in lower or "day after tomorrow" in lower:
        return 2
    
    # Check for "X din" or "X days"
    match = re.search(r"(\d+)\s*(din|days?)", lower)
    if match:
        return min(14, max(1, int(match.group(1))))
        
    if "salary" in lower or "next week" in lower:
        return 5
        
    return 3  # Default 3 days for general PAY_LATER

def generate_voice_response(intent: str, amount: float, customer_name: str, promise_days: int = 3) -> str:
    """Generates warm, natural Hinglish voice assistant audio dialogue."""
    amt_str = f"₹{amount:,.0f}" if amount else "payment"
    name_str = customer_name.split()[0] if customer_name else "Sir"

    if intent == "PAY_NOW":
        return f"Shukriya {name_str}! Maine aapke WhatsApp aur SMS par Razorpay ka secure payment link bhej diya hai. Aap wahan se 1-click mein UPI ya card se {amt_str} complete kar sakte hain."
    
    if intent == "PAY_LATER":
        return f"Bilkul {name_str}, maine note kar liya hai ki aap {promise_days} din baad payment karenge. Humne aapka Promise-to-Pay record update kar diya hai aur tab tak koi call nahi aayegi. Shukriya!"

    if intent == "PAYMENT_METHOD_PROBLEM":
        return f"Koi baat nahi {name_str}. Maine ek fresh smart link bheja hai jismein multiple payment options jaise UPI, NetBanking, aur alternative cards available hain. Ek baar try kijiye."

    if intent == "REFUSE":
        return f"Samajh gaya {name_str}. Aapki request note kar li gayi hai aur hum order cancel kar rahe hain. Aapko aage se is baare mein koi call ya message nahi aayega. Dhanyavaad."

    if intent == "HUMAN_ESCALATION":
        return f"Zaroor {name_str}, main turant yeh case humare senior account manager ko connect kar raha hoon. Woh aapko thodi der mein call karenge."

    if intent == "CANNOT_PAY":
        return f"Hum samajhte hain {name_str}. Main yeh details merchant ko review ke liye bhej raha hoon taaki agar koi customized installment ya discount plan ho toh aapko offer kar sakein."

    return f"Ji {name_str}, kya aap batayenge ki aap payment abhi karna chahenge ya koi aur help chahiye?"

def classify_voice_transcript(transcript: str, amount: float = 0.0, customer_name: str = "") -> Dict[str, Any]:
    """
    Primary voice NLU entrypoint:
    Tries Gemini API first for rich natural language context; falls back to deterministic regex.
    """
    if not transcript or not transcript.strip():
        return {
            "intent": "UNCLEAR",
            "confidence": 0.0,
            "classifier": "empty_transcript",
            "spoken_response": "Aapki aawaz theek se sunai nahi di, kya aap dobara bol sakte hain?",
            "candidate_action": "UNCLEAR",
            "promise_days": 0
        }

    # Attempt Gemini classification
    prompt = f"""Classify this voice customer transcript into exactly one intent for a payment recovery workflow:
Transcript: "{transcript}"

Candidate intents:
- PAY_NOW: customer wants to pay immediately or requests link
- PAY_LATER: customer promises to pay later (after salary, tomorrow, next week)
- PAYMENT_METHOD_PROBLEM: customer reports card/UPI failure or asks for another method
- CANNOT_PAY: customer lacks money or cannot afford payment
- REFUSE: customer explicitly cancels, refuses, or asks to stop calling
- HUMAN_ESCALATION: customer requests to talk to a human agent/manager
- UNCLEAR: unintelligible, irrelevant, or ambiguous

Return JSON format:
{{
  "intent": "INTENT_NAME",
  "confidence": 0.95,
  "promise_days": 3,
  "explanation": "brief reason"
}}"""

    gemini_res = query_gemini_json(prompt)
    if gemini_res and gemini_res.get("intent") in INTENTS:
        intent = gemini_res["intent"]
        confidence = float(gemini_res.get("confidence", 0.90))
        promise_days = int(gemini_res.get("promise_days") or extract_promise_offset_days(transcript))
        classifier = "gemini_model"
    else:
        det = deterministic_classify(transcript)
        intent = det["intent"]
        confidence = det["confidence"]
        promise_days = extract_promise_offset_days(transcript) if intent == "PAY_LATER" else 0
        classifier = det["classifier"]

    # Map intent to candidate action
    action_map = {
        "PAY_NOW": "CREATE_PAYMENT_LINK",
        "PAY_LATER": "RECORD_PROMISE_TO_PAY",
        "PAYMENT_METHOD_PROBLEM": "CREATE_PAYMENT_LINK",
        "REFUSE": "STOP",
        "HUMAN_ESCALATION": "ESCALATE",
        "CANNOT_PAY": "ESCALATE",
        "UNCLEAR": "UNCLEAR"
    }
    candidate_action = action_map.get(intent, "UNCLEAR")
    spoken_response = generate_voice_response(intent, amount, customer_name, promise_days)

    return {
        "intent": intent,
        "confidence": confidence,
        "classifier": classifier,
        "promise_days": promise_days,
        "candidate_action": candidate_action,
        "spoken_response": spoken_response
    }
