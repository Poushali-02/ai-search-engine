import os
import google.generativeai as genai
from dotenv import load_dotenv
import random

load_dotenv()

model = genai.GenerativeModel("gemini-1.5-pro-latest")  # or your preferred version

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment variables.")

genai.configure(api_key=api_key)


# Optional: randomized follow-up prompts for natural conversation
FOLLOW_UP_QUESTIONS = {
    "explore": [
        "Would you like to explore this further?",
        "Want me to break it down more?",
        "Should I expand on that?",
        "Would a detailed explanation help here?",
        "Curious about the 'why' behind this?",
        "Would a deeper dive into this topic help?",
        "Shall I walk you through this step-by-step?",
    ],
    "examples": [
        "Need an example to make it clearer?",
        "Shall I walk you through a sample scenario?",
        "Would a real-world analogy help here?",
        "Would you like a visual or analogy to understand it better?",
        "Want to hear how this works in real life?",
        "Should I explain this like you're five?",
    ],
    "connections": [
        "Want to know how this connects to something bigger?",
        "Would you like the advanced version of this?",
        "Want me to show how this works with real data?",
        "Want a nerdy detail? I’ve got one.",
        "Feeling curious? I can go on!",
        "Want to geek out on this a bit more?"
    ],
    "decisions": [
        "Would it help if I listed pros and cons?",
        "Need help choosing between similar options?",
        "Want help choosing between options?",
        "Should I compare a few approaches?",
        "Shall I summarize the key takeaways?",
    ],
    "style_variation": [
        "Want to hear the quick version and then the in-depth one?",
        "Would you prefer a comparison to something familiar?",
    ],
    "friendly": [
        "Want to keep chatting about this?",
        "Would you like a fun fact connected to this?",
    ]
}



def search_with_gemini(user_input: str, chat_memory: list = None) -> str:
    if not user_input.strip():
        return "Please enter a valid question."

    try:
        # Construct prompt context from memory
        context = ""
        if chat_memory:
            for exchange in chat_memory:
                context += f"User: {exchange['user_input']}\nAssistant: {exchange['bot_response']}\n"
        
        # Choose a random follow-up
        category = random.choice(list(FOLLOW_UP_QUESTIONS.keys()))
        follow_up = random.choice(FOLLOW_UP_QUESTIONS[category])
        prompt = f"""
You are an intelligent, friendly AI assistant built for answering questions clearly and helpfully. 
Use Markdown formatting: **bold** for important words, *italic* for highlights, and headings where helpful.

Here’s what the user and assistant have talked about so far:
{context}
Now, they asked: {user_input}

Instructions:
1. Respond concisely, starting with the most relevant point.
2. If the question could benefit from a deeper explanation, end your response with: "{follow_up}"
3. Keep your tone warm, direct, and helpful.
        """

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 1.2,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048
            }
        )

        return response.text if response and response.text else "Sorry, I couldn't find a good answer."

    except Exception as e:
        return f"Error: {str(e)}"
