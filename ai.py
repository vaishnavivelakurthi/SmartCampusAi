import os
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

# Load variables from .env
load_dotenv()

def get_ai_config() -> tuple[str, str, str]:
    """Retrieves AI API configuration from session state overrides or .env."""
    override = st.session_state.get("api_override", {})
    
    api_key = override.get("api_key") or os.getenv("API_KEY")
    model_name = override.get("model_name") or os.getenv("MODEL_NAME") or "gpt-4o-mini"
    base_url = override.get("base_url") or os.getenv("BASE_URL") or "https://api.openai.com/v1"
    
    # Strip whitespaces
    if api_key:
        api_key = api_key.strip()
    if base_url:
        base_url = base_url.strip()
    if model_name:
        model_name = model_name.strip()
        
    return api_key, model_name, base_url

def generate_chat_response(messages: list[dict]) -> tuple[bool, str]:
    """Sends a chat message history to the API and returns the generated response."""
    api_key, model_name, base_url = get_ai_config()
    
    if not api_key:
        return (
            False, 
            "**API Configuration Required:** The API key is missing. Please go to the **Settings** page in the sidebar to configure your credentials or add `API_KEY` to your local `.env` file."
        )
        
    try:
        # Initialize OpenAI Client (OpenAI SDK v1.0.0+)
        client = OpenAI(api_key=api_key, base_url=base_url)
        
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.7,
            max_tokens=1500
        )
        
        reply = response.choices[0].message.content
        return True, reply
        
    except Exception as e:
        err_msg = str(e)
        # Format user friendly message depending on typical error strings
        if "API key" in err_msg or "401" in err_msg or "Incorrect API key" in err_msg:
            friendly_err = "Authentication Failed: The provided API key is invalid. Please double check your credentials."
        elif "connection" in err_msg.lower() or "timeout" in err_msg.lower():
            friendly_err = "Network Connection Error: Could not connect to the API server. Please check your internet connection."
        else:
            friendly_err = f"API Error: {err_msg}"
            
        return False, friendly_err
