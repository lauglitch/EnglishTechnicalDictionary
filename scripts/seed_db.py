import json
from app.database import SessionLocal
from app import models
from app.models import Word
from datetime import datetime

DB_FILE = "test_data.json"


def seed_database():
    db = SessionLocal()

    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        exists = db.query(Word).filter(Word.word == item["word"]).first()

        if exists:
            print(f"Skipping existing word: {item['word']}")
            continue

        word = Word(
            word=item["word"],
            definition=item["definition"],
            grammar_class=item.get("grammar_class"),
            topic=item.get("topic"),
            example=item.get("example"),
            author=item.get("author", "Admin"),
            status=item.get("status", "approved"),
            created_at=datetime.utcnow(),
        )

        db.add(word)

    db.commit()
    db.close()

    print("Database seeded successfully")


if __name__ == "__main__":
    seed_database()
