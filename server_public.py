import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import requests as http_requests

from src.models import Session, Turn, new_session_id
from src.classifier import classify_and_update
from src.analyzer import full_report
from src.store import save_session, load_session, load_all_sessions, list_session_ids

load_dotenv()

app = Flask(__name__, static_folder='frontend/build', static_url_path='')
CORS(app)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

@app.errorhandler(404)
def not_found(e):
    return send_from_directory(app.static_folder, 'index.html')


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.json
    messages = data.get("messages", [])
    model = data.get("model", "llama-3.3-70b-versatile")

    system_prompt = {
        "role": "system",
        "content": (
            "You are a helpful coding assistant in a research study about human-LLM collaboration. "
            "After every response, add a <meta> JSON block with:\n"
            '  "confidence": (1-5 integer),\n'
            '  "uncertainty_areas": (list of strings),\n'
            '  "constraints_followed": (list of strings)\n'
            "Wrap it exactly like: <meta>{...}</meta>\n"
            "Always be honest about your uncertainty."
        ),
    }

    full_messages = [system_prompt] + messages

    try:
        resp = http_requests.post(
            GROQ_URL,
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={"model": model, "messages": full_messages, "temperature": 0.7, "max_tokens": 2048},
            timeout=30,
        )
        resp.raise_for_status()
        result = resp.json()
        assistant_content = result["choices"][0]["message"]["content"]

        meta = {}
        if "<meta>" in assistant_content and "</meta>" in assistant_content:
            try:
                meta_str = assistant_content.split("<meta>")[1].split("</meta>")[0]
                meta = json.loads(meta_str)
            except (json.JSONDecodeError, IndexError):
                meta = {}

        return jsonify({"content": assistant_content, "meta": meta, "model": model})

    except http_requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 502


@app.route("/api/sessions", methods=["GET"])
def get_sessions():
    sessions = load_all_sessions()
    return jsonify([s.to_dict() for s in sessions])


@app.route("/api/sessions/<session_id>", methods=["GET"])
def get_session(session_id):
    s = load_session(session_id)
    if s is None:
        return jsonify({"error": "Not found"}), 404
    return jsonify(s.to_dict())


@app.route("/api/sessions", methods=["POST"])
def create_session():
    data = request.json
    session = Session(
        session_id=data.get("session_id", new_session_id()),
        task_type=data.get("task_type", "generation"),
        turns=[Turn.from_dict(t) for t in data.get("turns", [])],
        outcome=data.get("outcome", "partial"),
        task_description=data.get("task_description", ""),
        timestamp=data.get("timestamp", datetime.now().isoformat()),
    )
    classify_and_update(session)
    path = save_session(session)
    return jsonify({"status": "saved", "session_id": session.session_id, "pattern": session.final_pattern, "path": path}), 201


@app.route("/api/report", methods=["GET"])
def report():
    sessions = load_all_sessions()
    result = full_report(sessions)
    os.makedirs("outputs", exist_ok=True)
    with open("outputs/report.json", "w") as f:
        json.dump(result, f, indent=2)
    return jsonify(result)


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({"status": "ok", "sessions_count": len(list_session_ids())})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    print(f"Starting server on port {port}")
    app.run(debug=False, host='0.0.0.0', port=port)
