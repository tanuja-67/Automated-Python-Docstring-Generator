import os
import google.generativeai as genai
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Collect all available Google and OpenAI keys
GOOGLE_KEYS = [
    os.getenv("GOOGLE_API_KEY_1"),
    os.getenv("GOOGLE_API_KEY_2"),
    os.getenv("GOOGLE_API_KEY_3"),
]
GOOGLE_KEYS = [key for key in GOOGLE_KEYS if key]  # Filter out None values

OPENAI_KEY = os.getenv("OPENAI_API_KEY")

# Create alternating key rotation: Google 1, OpenAI, Google 2, OpenAI, Google 3, OpenAI
ALL_KEYS = []
max_keys = max(len(GOOGLE_KEYS), 1)
for i in range(max_keys):
    if i < len(GOOGLE_KEYS):
        ALL_KEYS.append(("google", GOOGLE_KEYS[i]))
    if OPENAI_KEY:
        ALL_KEYS.append(("openai", OPENAI_KEY))

OPENAI_CLIENT = OpenAI(api_key=OPENAI_KEY) if OPENAI_KEY else None

# Global counter for round-robin key selection
_current_key_index = 0

def generate_with_fallback(prompt: str) -> str:
    """Generate content using keys in round-robin rotation for load balancing."""
    global _current_key_index
    
    if not ALL_KEYS:
        return "API Error: No API keys configured"
    
    num_keys = len(ALL_KEYS)
    start_index = _current_key_index
    
    # Try each key starting from current rotation position
    for attempt in range(num_keys):
        current_index = (_current_key_index + attempt) % num_keys
        key_type, key_value = ALL_KEYS[current_index]
        
        try:
            if key_type == "google":
                genai.configure(api_key=key_value)
                model = genai.GenerativeModel("models/gemini-flash-lite-latest")
                response = model.generate_content(prompt)
                # Move to next key for next call (round-robin)
                _current_key_index = (current_index + 1) % num_keys
                return response.text
            
            elif key_type == "openai" and OPENAI_CLIENT:
                response = OPENAI_CLIENT.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[{"role": "user", "content": prompt}]
                )
                # Move to next key for next call (round-robin)
                _current_key_index = (current_index + 1) % num_keys
                return response.choices[0].message.content
        
        except Exception as e:
            # Key failed, try next one
            if attempt == num_keys - 1:
                # All keys exhausted
                return f"API Error: All keys failed. Last error: {str(e)}"
            continue
    
    return "API Error: Unexpected error in key rotation"
