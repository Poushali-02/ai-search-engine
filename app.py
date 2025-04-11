from flask import Flask, render_template, request, jsonify
import sqlite3
from dotenv import load_dotenv
from search import search_with_gemini

load_dotenv()

app = Flask(__name__)

#chat history stored in a database

DB_NAME = 'history.db'

def _init_db():
    conn = sqlite3.connect(DB_NAME)
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
    conn.close()

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
        
        response = search_with_gemini(user_input)
    
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