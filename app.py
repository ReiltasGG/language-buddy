from flask import Flask, render_template, request, jsonify
import requests
import json
from database import init_db, record_answer, get_stats, get_review_cards, reset_progress

app = Flask(__name__)
init_db()


def get_system_prompt(language):
    return f"""You are a friendly {language} language tutor having a conversation with a beginner learner.
- Respond primarily in {language} but keep it simple and beginner friendly
- After your {language} response, add a section starting with "📝 Notes:" where you:
  - Provide an English translation of what you said
  - Gently correct any mistakes the user made in their message
  - Explain any important grammar or vocabulary briefly
- Keep responses short and encouraging
- If the user writes in English, respond in both {language} and English to model the language"""


def get_flashcard_prompt(language, category):
    category_descriptions = {
        "verbs": "common action verbs",
        "places": "common places and location names",
        "nouns": "common everyday nouns",
        "kanji": "basic kanji characters with their core meanings",
        "hangul": "basic Hangul characters or syllables with their romanization and meaning",
        "hanzi": "basic Hanzi characters with their pinyin and core meanings",
    }

    desc = category_descriptions.get(category, "common words")

    if category == "kanji":
        return f"""Generate 10 Japanese flashcards for {desc}.
For kanji cards do NOT include furigana since the user is practicing reading kanji.

Return ONLY a JSON array, no explanation, no markdown:
[
  {{"japanese": "日", "furigana": "", "display": "日", "english": "sun / day"}},
  ...
]"""

    elif category == "hangul":
        return f"""Generate 10 Korean flashcards for basic Hangul characters or syllables.
Include the romanization as the furigana equivalent.

Return ONLY a JSON array, no explanation, no markdown:
[
  {{"japanese": "가", "furigana": "ga", "display": "가", "english": "syllable: ga"}},
  ...
]"""

    elif category == "hanzi":
        return f"""Generate 10 Mandarin flashcards for basic Hanzi characters.
Include pinyin as the furigana equivalent.

Return ONLY a JSON array, no explanation, no markdown:
[
  {{"japanese": "日", "furigana": "rì", "display": "日", "english": "sun / day"}},
  ...
]"""

    else:
        return f"""Generate 10 {language} flashcards for {desc}.
Include the {language} word, its romanization or pronunciation guide as furigana (if applicable), and the English translation.

Return ONLY a JSON array, no explanation, no markdown:
[
  {{"japanese": "{language} word here", "furigana": "pronunciation if applicable, else empty string", "display": "{language} word here", "english": "english translation"}},
  ...
]

For languages that use the Latin alphabet (Spanish, French, Italian, Portuguese, German), set furigana to an empty string."""


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    message = data.get("message", "")
    language = data.get("language", "Japanese")
    history = data.get("history", [])

    system_prompt = get_system_prompt(language)

    conversation = f"System: {system_prompt}\n\n"
    for msg in history[-4:]:
        role = "User" if msg["role"] == "user" else "Assistant"
        conversation += f"{role}: {msg['content']}\n"
    conversation += f"User: {message}\nAssistant:"

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "gemma3:4b",
            "prompt": conversation,
            "stream": False
        }, timeout=60)

        reply = response.json()["response"].strip()
        return jsonify({"reply": reply, "error": None})

    except Exception as e:
        return jsonify({"reply": None, "error": str(e)})


@app.route("/flashcards", methods=["POST"])
def get_flashcards():
    data = request.json
    language = data.get("language", "Japanese")
    category = data.get("category", "nouns")

    prompt = get_flashcard_prompt(language, category)

    try:
        response = requests.post("http://localhost:11434/api/generate", json={
            "model": "gemma3:4b",
            "prompt": prompt,
            "stream": False
        }, timeout=60)

        raw = response.json()["response"].strip()
        clean = raw.replace("```json", "").replace("```", "").strip()
        cards = json.loads(clean)
        return jsonify({"cards": cards, "error": None})

    except Exception as e:
        return jsonify({"cards": [], "error": str(e)})


@app.route("/record", methods=["POST"])
def record():
    data = request.json
    record_answer(
        data["language"],
        data["category"],
        data["japanese"],
        data["english"],
        data["correct"]
    )
    return jsonify({"success": True})


@app.route("/stats/<language>")
def stats(language):
    return jsonify(get_stats(language))


@app.route("/review/<language>")
def review(language):
    cards = get_review_cards(language)
    return jsonify({"cards": cards})


@app.route("/reset/<language>", methods=["POST"])
def reset(language):
    reset_progress(language)
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)