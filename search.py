import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

model = genai.GenerativeModel("gemini-1.5-pro-latest")  # or your preferred version

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)
def search_with_gemini(user_input: str) -> str:
    # Ensure input is not empty
    if not user_input or not user_input.strip():
        return "Error: Your input was empty. Please enter a valid question."

    try:
        prompt = f"""
You are an intelligent AI assistant. Format your responses using Markdown:

- Use **bold** for important points
- Use *italic* for highlights
- Use headings (#, ##, ###) where needed
- Be clear, helpful, and concise

Question: {user_input}
        """.strip()

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 1.2,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048
            }
        )

        # Ensure response is not None
        return response.text if response and response.text else "Sorry, I couldn't generate a response."

    except Exception as e:
        return f"Error: {str(e)}"