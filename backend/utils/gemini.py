import os
from google import genai
from config import GEMINI_API_KEY

def get_gemini_client():
    if not GEMINI_API_KEY:
        return None
    try:
        # Uses GEMINI_API_KEY directly
        return genai.Client(api_key=GEMINI_API_KEY)
    except Exception:
        return None

def generate_text(prompt: str, system_instruction: str = None) -> str:
    client = get_gemini_client()
    if not client:
        return ""
    
    try:
        config = {}
        if system_instruction:
            config["system_instruction"] = system_instruction
            
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
            config=config
        )
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {str(e)}")
        return ""
