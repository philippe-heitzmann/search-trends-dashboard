import logging

from openai import OpenAI
from dotenv import load_dotenv

import os

load_dotenv()

logging.basicConfig(level=logging.INFO)

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI()
client.api_key = OPENAI_API_KEY

def query_chatgpt(prompt: str,
                  model="gpt-4o-mini") -> str:
    """
    Calls the OpenAI ChatGPT API with the given prompt and returns the response.

    Parameters:
    prompt (str): The prompt to send to the ChatGPT API.

    Returns:
    str: The response from the ChatGPT API.
    "gpt-4o-2024-05-13"
    """
    try:
        response = client.chat.completions.create(
            model=model,
            stream=False,
            messages=[{"role": "user", "content": f"Prompt: {prompt}"}],
            temperature=0.7
        )
        logging.debug(f"Successfully received response from ChatGPT API")
        return response.choices[0].message.content.strip()
    except Exception as e:
        error_type = type(e).__name__
        error_msg = str(e)
        logging.error(f"Failed to query ChatGPT - Error Type: {error_type}")
        logging.error(f"Error Message: {error_msg}")
        logging.error(f"Model used: {model}")
        logging.error(f"Prompt length: {len(prompt)} characters")
        
        # Log specific OpenAI API errors if available
        if hasattr(e, 'response'):
            if hasattr(e.response, 'status_code'):
                logging.error(f"API Status Code: {e.response.status_code}")
            if hasattr(e.response, 'json'):
                try:
                    error_details = e.response.json()
                    logging.error(f"API Error Details: {error_details}")
                except:
                    logging.error("Could not parse API error response as JSON")
        
        # Re-raise the exception after logging
        raise

def save_text(content: str, filepath: str) -> None:
    """
    Saves text content to a file with error handling.
    
    Args:
        content: Text content to save
        filepath: Path where the file should be saved
    """
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        logging.info(f"File saved to {filepath}")
    except IOError as e:
        print(f"Error saving file {filepath}: {e}")