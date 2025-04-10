from flask import Flask, render_template, request, jsonify
import sqlite3
import os
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
    return render_template("index.html")

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    user_input = data.get('user_input')
    if not user_input:
        return jsonify({"error": "No input provided"}), 400
    response = search_with_gemini(user_input)
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO chat_history (user_input, bot_response) VALUES (?, ?)", (user_input, response))
    conn.commit()
    conn.close()
    return jsonify({"response": response})

if __name__ == "__main__":
    _init_db()
    app.run(debug=True)