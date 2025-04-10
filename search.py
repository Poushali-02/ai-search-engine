import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-pro-latest")  # or your preferred version


def search_with_gemini(user_input: str) -> str:
    try:
        response = model.generate_content(
            user_input,
            generation_config={
                "temperature": 1.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048
            }
        )
        return response.text
    except Exception as e:
        return f"Error: {str(e)}"