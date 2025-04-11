import os
import google.generativeai as genai
from dotenv import load_dotenv
import random
import requests

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

# Expanded trigger keywords
trigger_keywords = [
    "explain", "how", "why", "step", "details", "example", "in-depth", "deep", "more info", "what is",
    "can you elaborate", "could you explain", "please elaborate", "elaborate", "tell me more", 
    "go deeper", "walk me through", "full explanation", "detailed", "clarify", "clarification", 
    "expand on", "break it down", "overview", "introduction to", "help me understand", 
    "simplify", "demystify", "teach me", "layman", "easy explanation", "basic", "fundamentals of", 
    "I don’t understand", "I’m confused", "I’m curious", "need context", "context", 
    "what does it mean", "meaning of", "beginner", "from scratch", "starting from", "what do you mean",
    "deeper", "technical", "can you describe", "what happens when", "how does it work"
]

def needs_deep_answer(user_input: str) -> bool:
    return any(word in user_input.lower() for word in trigger_keywords)

def detect_intent(user_input: str) -> str:
    lowered = user_input.lower()
    if any(kw in lowered for kw in ["compare", "vs", "difference between", "pros and cons"]):
        return "compare"
    elif any(kw in lowered for kw in ["example", "analogy", "illustrate"]):
        return "examples"
    elif any(kw in lowered for kw in ["connect", "relation", "linked", "association"]):
        return "connections"
    elif any(kw in lowered for kw in trigger_keywords):
        return "explore"
    else:
        return "friendly"

def search_duckduckgo(query: str) -> str:
    try:
        url = f"https://api.duckduckgo.com/?q={query}&format=json&no_html=1&skip_disambig=1"
        response = requests.get(url, timeout=5)
        data = response.json()

        if data.get("AbstractText"):
            return data["AbstractText"]
        elif data.get("RelatedTopics"):
            for topic in data["RelatedTopics"]:
                if isinstance(topic, dict) and topic.get("Text"):
                    return topic["Text"]
        return "I couldn't find a good answer on that. Want me to dig deeper?"
    except Exception as e:
        return f"Error accessing DuckDuckGo: {str(e)}"

chat_memory = []

MAX_MEMORY = 10
def search_with_gemini(user_input: str, chat_memory: list) -> str:
    if not user_input.strip():
        return "Please enter a valid question."

    try:
        # Follow-up trigger responses from user
        FOLLOW_UP_RESPONSES = [
            "yes", "please explain", "go deeper", "elaborate", "sure", "of course", "continue",
            "more info", "keep going", "i’m interested", "yes, please", "want to learn",
            "do explain", "want to know more", "tell me more", "please do", "what else"
        ]

        # Detect if the last Gemini response had a follow-up question
        last_bot_response = chat_memory[-1]["bot_response"].lower() if chat_memory else ""
        last_followup_asked = any(
            fu.lower() in last_bot_response
            for questions in FOLLOW_UP_QUESTIONS.values()
            for fu in questions
        )

        # Detect if user is replying with a follow-up intent
        user_followup_reply = any(resp in user_input.lower() for resp in FOLLOW_UP_RESPONSES)

        # DuckDuckGo FIRST (if no deep question AND not a follow-up confirmation)
        if not needs_deep_answer(user_input) and not (last_followup_asked and user_followup_reply):
            response = search_duckduckgo(user_input)
            if "dig deeper" not in response.lower():
                chat_memory.append({
                    "user_input": user_input,
                    "bot_response": response
                })
                if len(chat_memory) > MAX_MEMORY:
                    chat_memory.pop(0)
                return response

        # Build memory context
        context = ""
        for exchange in chat_memory[-MAX_MEMORY:]:
            context += f"User: {exchange['user_input']}\nAssistant: {exchange['bot_response']}\n"

        # Detect intent for appropriate follow-up
        intent = detect_intent(user_input)
        is_follow_up = needs_deep_answer(user_input)
        follow_up = random.choice(FOLLOW_UP_QUESTIONS.get(intent, [])) if FOLLOW_UP_QUESTIONS.get(intent) else ""

        # Prompt Gemini
        # 4. Prompt Gemini with enhanced behavior
        prompt = f"""
You are a helpful, smart, and friendly assistant. Use a warm and conversational tone. Always respond with Markdown (**bold**, *italics*, `code`, lists, etc.).

Conversation so far:
{context}

User just asked: {user_input}

Instructions:
- {"This is a follow-up. Give a detailed, in-depth explanation with steps, examples, and technical clarity." if is_follow_up else "Give a concise but helpful answer first."}
- Make the response natural, like a friendly guide.
- Use Markdown formatting for clarity.
- {"Don't ask follow-up again; the user already showed interest." if is_follow_up else f"End with: {follow_up}"}
"""

        response = model.generate_content(
            prompt,
            generation_config={
                "temperature": 0.7,
                "top_p": 1,
                "top_k": 1,
                "max_output_tokens": 2048
            }
        )

        result = response.text.strip() if response and response.text else "Sorry, I couldn't find a good answer."

        # Store in memory
        chat_memory.append({
            "user_input": user_input,
            "bot_response": result
        })
        if len(chat_memory) > MAX_MEMORY:
            chat_memory.pop(0)

        return result

    except Exception as e:
        return f"Error: {str(e)}"
