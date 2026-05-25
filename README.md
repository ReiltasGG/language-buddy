# 🌍 Language Buddy

A local, AI-powered language learning app that runs entirely on your machine. Practice conversational skills with a friendly tutor and reinforce vocabulary with interactive flashcards — no cloud API required.

---

## Features

- **Conversational Tutor** — Chat in your target language with an AI tutor that responds in the target language, provides English translations, corrects mistakes, and explains grammar.
- **Flashcard Mode** — Generate vocabulary flashcards on demand across categories like nouns, verbs, places, and script-specific sets (Kanji, Hangul, Hanzi).
- **8 Supported Languages** — Japanese 🇯🇵, Spanish 🇪🇸, French 🇫🇷, Mandarin 🇨🇳, Italian 🇮🇹, Portuguese 🇧🇷, German 🇩🇪, Korean 🇰🇷
- **Fully Local** — Powered by [Ollama](https://ollama.com) running `gemma3:4b` on your own hardware. No data leaves your machine.

---

## Project Structure

```
language-buddy/
├── app.py          # Flask backend — chat and flashcard API routes
└── templates/
    └── index.html  # Single-page frontend (vanilla JS + CSS)
```

---

## Requirements

- Python 3.8+
- [Ollama](https://ollama.com) with the `gemma3:4b` model pulled

---

## Setup

**1. Clone the repo**
```bash
git clone https://github.com/ReiltasGG/language-buddy.git
cd language-buddy
```

**2. Install Python dependencies**
```bash
pip install flask requests
```

**3. Pull the model via Ollama**
```bash
ollama pull gemma3:4b
```

**4. Start Ollama** (if it isn't already running)
```bash
ollama serve
```

**5. Run the app**
```bash
python app.py
```

**6. Open your browser**
```
http://localhost:5001
```

---

## Usage

### Chat Mode
Select a language from the dropdown, then type a message to start a conversation. The tutor will:
- Reply in the target language at a beginner-friendly level
- Provide a **📝 Notes** section with an English translation, error corrections, and grammar tips

### Flashcard Mode
Switch to the **Flashcards** tab, pick a vocabulary category, and flip through AI-generated cards. Mark each card correct or incorrect to track your score for the session.

**Flashcard categories by language:**

| Category | Description |
|----------|-------------|
| Nouns | Everyday objects and concepts |
| Verbs | Common action words |
| Places | Locations and destinations |
| Kanji | Japanese characters (no furigana — reading practice) |
| Hangul | Korean syllables with romanization |
| Hanzi | Mandarin characters with pinyin |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | Serves the frontend |
| `POST` | `/chat` | Sends a message to the tutor; returns a reply |
| `POST` | `/flashcards` | Generates a set of 10 flashcards for a given language and category |

### `/chat` request body
```json
{
  "message": "こんにちは！",
  "language": "Japanese",
  "history": [{ "role": "user", "content": "..." }, ...]
}
```

### `/flashcards` request body
```json
{
  "language": "Japanese",
  "category": "kanji"
}
```

---

## Troubleshooting

**"Could not connect" error in the UI**
Make sure both Flask (`python app.py`) and Ollama (`ollama serve`) are running before opening the app.

**Slow responses**
Response speed depends on your hardware. `gemma3:4b` is a lightweight model, but a GPU will significantly improve performance. You can swap in a different Ollama model by changing the `"model"` field in `app.py`.

**Flashcards not generating**
Ensure the `gemma3:4b` model has been pulled (`ollama pull gemma3:4b`) and Ollama is running on `http://localhost:11434`.

---

## License

MIT