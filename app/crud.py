# DB LOGIC
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException
from datetime import datetime

from app import schemas
from app import models
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

    # MAP AI → STATUS
    if analysis["approved_by_ai"]:
        status = "approved"
    elif "unsafe_content" in analysis["flags"]:
        status = "rejected"
    else:
        status = "pending"

    print("AI moderation:", analysis)

    try:
        db_word = models.Word(
            word=word.word,
            definition=word.definition,
            example=word.example,
            topic=word.topic,
            author_id=user_id,
            grammar_class=word.grammar_class,
            status=status,
            created_at=datetime.utcnow(),
        )

        db.add(db_word)
        db.commit()
        db.refresh(db_word)

        return db_word

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


# ---------------- GET BY NAME ----------------
def get_word_by_name(db: Session, word_str: str):
    return (
        db.query(models.Word)
        .filter(func.lower(models.Word.word) == word_str.lower())
        .first()
    )


# ---------------- GET ALL ----------------
def get_words(db: Session, skip: int = 0, limit: int = 10):
    query = db.query(models.Word).filter(models.Word.status == "approved")

    total = query.count()

    items = query.order_by(models.Word.word.asc()).offset(skip).limit(limit).all()

    return {"items": items, "total": total}


# ---------------- DELETE WORD ----------------
def delete_word_by_name(db: Session, word_str: str):
    word = get_word_by_name(db, word_str)

    if not word:
        return None

    db.delete(word)
    db.commit()
    return True


# ---------------- UPDATE WORD ----------------
def update_word_fields(db: Session, word_str: str, data: dict):

    word = get_word_by_name(db, word_str)

    if not word:
        return None

    for key, value in data.items():
        if hasattr(word, key):
            setattr(word, key, value)

    db.commit()
    db.refresh(word)

    return word


# ---------------- RESET TEST DATA ----------------
def reset_test_data(db: Session):
    import json
    from pathlib import Path

    file_path = Path(__file__).parent / "test_data.json"

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="test_data.json not found")

    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Clear table
    db.query(models.Word).delete()

    # Reinsert
    for w in data:
        try:
            db_word = models.Word(
                word=w.get("word"),
                definition=w.get("definition"),
                example=w.get("example"),
                topic=w.get("topic"),
                grammar_class=w.get("grammar_class", "noun"),
                author=w.get("author", "Admin"),
                status="approved",
                created_at=datetime.utcnow(),
            )

            db.add(db_word)

        except Exception as e:
            print("RESET ERROR:", e)

    db.commit()

    return len(data)
