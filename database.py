import sqlite3
import os

DB_FILE = os.path.join(os.path.dirname(__file__), "progress.db")


def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS flashcard_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language TEXT NOT NULL,
            category TEXT NOT NULL,
            japanese TEXT NOT NULL,
            furigana TEXT DEFAULT '',
            english TEXT NOT NULL,
            correct INTEGER DEFAULT 0,
            incorrect INTEGER DEFAULT 0,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # add furigana column if it doesn't exist (for existing databases)
    try:
        conn.execute("ALTER TABLE flashcard_progress ADD COLUMN furigana TEXT DEFAULT ''")
    except:
        pass
    conn.commit()
    conn.close()


def record_answer(language, category, japanese, furigana, english, correct):
    conn = get_db()
    row = conn.execute("""
        SELECT id FROM flashcard_progress
        WHERE language = ? AND category = ? AND japanese = ?
    """, (language, category, japanese)).fetchone()

    if row:
        if correct:
            conn.execute("""
                UPDATE flashcard_progress
                SET correct = correct + 1, last_seen = CURRENT_TIMESTAMP, furigana = ?
                WHERE id = ?
            """, (furigana, row["id"]))
        else:
            conn.execute("""
                UPDATE flashcard_progress
                SET incorrect = incorrect + 1, last_seen = CURRENT_TIMESTAMP, furigana = ?
                WHERE id = ?
            """, (furigana, row["id"]))
    else:
        conn.execute("""
            INSERT INTO flashcard_progress (language, category, japanese, furigana, english, correct, incorrect)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (language, category, japanese, furigana, english, 1 if correct else 0, 0 if correct else 1))

    conn.commit()
    conn.close()


def get_stats(language):
    conn = get_db()

    overall = conn.execute("""
        SELECT
            SUM(correct) as total_correct,
            SUM(incorrect) as total_incorrect,
            COUNT(*) as total_cards
        FROM flashcard_progress
        WHERE language = ?
    """, (language,)).fetchone()

    categories = conn.execute("""
        SELECT
            category,
            SUM(correct) as correct,
            SUM(incorrect) as incorrect,
            COUNT(*) as cards
        FROM flashcard_progress
        WHERE language = ?
        GROUP BY category
    """, (language,)).fetchall()

    hardest = conn.execute("""
        SELECT japanese, furigana, english, category, correct, incorrect
        FROM flashcard_progress
        WHERE language = ? AND incorrect > 0
        ORDER BY incorrect DESC
        LIMIT 10
    """, (language,)).fetchall()

    conn.close()

    return {
        "overall": dict(overall) if overall else {},
        "categories": [dict(c) for c in categories],
        "hardest": [dict(h) for h in hardest]
    }


def get_review_cards(language):
    conn = get_db()
    cards = conn.execute("""
        SELECT japanese, furigana, english, category,
               correct, incorrect,
               CAST(incorrect AS FLOAT) / (correct + incorrect) as error_rate
        FROM flashcard_progress
        WHERE language = ? AND incorrect > 0
        ORDER BY error_rate DESC
        LIMIT 20
    """, (language,)).fetchall()
    conn.close()
    return [dict(c) for c in cards]


def reset_progress(language):
    conn = get_db()
    conn.execute("DELETE FROM flashcard_progress WHERE language = ?", (language,))
    conn.commit()
    conn.close()