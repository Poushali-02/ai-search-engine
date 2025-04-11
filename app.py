from flask import Flask, render_template, request, jsonify, session
import sqlite3
import os
from dotenv import load_dotenv
from search import search_with_gemini

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY")
DB_NAME = 'history.db'

def _init_db():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute(
            '''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_input TEXT,
                bot_response TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        '''
        )
        conn.commit()
_init_db()

# routes

@app.route("/")
def main():
    with sqlite3.connect(DB_NAME) as conn:
        c = conn.cursor()
        c.execute("SELECT user_input, bot_response FROM chat_history ORDER BY timestamp ASC")
        history = [{"user_input": row[0], "bot_response": row[1]} for row in c.fetchall()]
    return render_template("index.html", history=history)
@app.route('/search', methods=['POST'])
def ask():
    try:
        data = request.get_json()
        user_input = data.get('user_input')
        if not user_input:
            return jsonify({"error": "No input provided"}), 400
        chat_memory = session.get("chat_memory", [])
        response = search_with_gemini(user_input, chat_memory)
        chat_memory.append({"user_input": user_input, "bot_response": response})
        chat_memory = chat_memory[-6:]
        session["chat_memory"] = chat_memory
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT INTO chat_history (user_input, bot_response) VALUES (?, ?)", (user_input, response))
            conn.commit()
        return jsonify({"response": response})
    
    except Exception as e:
        print(f"Error during /search: {e}")
        return jsonify({"response": f"Error: {str(e)}"}), 500

if __name__ == "__main__":
    _init_db()
    app.run(debug=True)