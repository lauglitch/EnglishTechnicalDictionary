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

    # Normalize input
    word_text = word.word.strip()

    # Check duplicates (safe + case insensitive)
    existing = (
        db.query(models.Word)
        .filter(func.lower(models.Word.word) == word_text.lower())
        .first()
    )

    if existing:
        raise HTTPException(status_code=400, detail="Word already exists")

    # AI analysis (SAFE GUARD)
    try:
        analysis = analyze_word(
            word_text, word.definition, word.example or "", word.topic or ""
        )
    except Exception as e:
        # IMPORTANT: never break API due to AI failure
        analysis = {
            "grammar_class": "unknown",
            "score": 0.0,
            "flags": [],
            "approved_by_ai": False,
        }

    try:
        db_word = models.Word(
            word=word_text,
            definition=word.definition,
            example=word.example,
            topic=word.topic,
            # keep compatibility with your schema
            author=getattr(word, "author", "Admin"),
            grammar_class=analysis.get("grammar_class", "noun"),
            status="pending",
            created_at=datetime.utcnow(),
            # AI fields (only if they exist in model)
            ai_score=analysis.get("score"),
            ai_flags=(
                ",".join(analysis.get("flags", [])) if analysis.get("flags") else None
            ),
            ai_approved=analysis.get("approved_by_ai", False),
        )

        db.add(db_word)
        db.commit()
        db.refresh(db_word)

        return db_word

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"DB insert error: {str(e)}")


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
