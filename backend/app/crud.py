# DB LOGIC
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import datetime
from . import models, schemas
from app.services.moderation import analyze_word


# ---------------- CREATE ----------------
def create_word(db: Session, word: schemas.WordCreate, user_id: int):

    analysis = analyze_word(
        word.word, word.definition, word.example or "", word.topic or ""
    )

    existing = (
        db.query(models.Word)
        .filter(func.lower(models.Word.word) == word.word.lower())
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Word already exists")

    try:
        db_word = models.Word(
            word=word.word,
            definition=word.definition,
            example=word.example,
            topic=word.topic,
            author_id=user_id,
            grammar_class=analysis["grammar_class"],
            status="pending",
            created_at=None,
            ai_score=analysis["score"],
            ai_flags=",".join(analysis["flags"]) if analysis["flags"] else None,
            ai_approved=analysis["approved_by_ai"],
        )

        db.add(db_word)
        db.commit()
        db.refresh(db_word)

        return db_word

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- RESET TEST DATA ----------------
def reset_test_data(db):
    import json
    from pathlib import Path
    from datetime import datetime
    from . import models

    file_path = Path(__file__).parent / "test_data.json"

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    db.query(models.Word).delete()

    for w in data:
        try:
            db_word = models.Word(
                word=w.get("word"),
                definition=w.get("definition"),
                example=w.get("example"),
                topic=w.get("topic"),
                grammar_class=w.get("grammar_class", "noun"),
                author_id=None,
                status="approved",
                ai_score=1.0,
                ai_flags=None,
                ai_approved=True,
                created_at=datetime.utcnow(),
            )

            db.add(db_word)

        except Exception as e:
            print("RESET ERROR:", e)

    db.commit()

    return {"message": "reset ok"}
