from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from google.generativeai import GenerativeModel
import google.generativeai as genai
import os

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

app = Flask(__name__)
CORS(app, resources={r"/chat": {"origins": "*"}})

genai.configure(api_key=GOOGLE_API_KEY)
model = GenerativeModel("gemini-1.5-flash")
chat_histories = {}

@app.route("/models")
def list_models():
    models = genai.list_models()
    return jsonify([m.name for m in models])
@app.route("/chat", methods=["POST"])

def chat():
    try:
        data = request.get_json()
        user_id = data.get("user_id", "default_user")
        user_message = data["message"]

        if user_id not in chat_histories:
            chat_histories[user_id] = []
            initial_message = {
                "role": "user",
                "parts": ["You are a game recommendation assistant..."]
            }
            chat_histories[user_id].append(initial_message)
            model_response = model.generate_content(chat_histories[user_id])
            chat_histories[user_id].append({"role": "model", "parts": [model_response.text]})

        chat_histories[user_id].append({"role": "user", "parts": [user_message]})
        response = model.generate_content(chat_histories[user_id])
        model_message = response.text
        chat_histories[user_id].append({"role": "model", "parts": [model_message]})

        return jsonify({"reply": model_message})
    
    except Exception as e:
        print("Error:", str(e))
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)