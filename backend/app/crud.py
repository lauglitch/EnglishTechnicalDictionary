from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
from pathlib import Path
import json
from fastapi import HTTPException
from datetime import datetime


# CREATE
def create_word(db: Session, word: schemas.WordCreate, user_id: int):
    existing = (
        db.query(models.Word)
        .filter(func.lower(models.Word.word) == word.word.lower())
        .first()
    )
    if existing:
        return None
    try:
        db_word = models.Word(
            word=word.word,
            definition=word.definition,
            grammar_class=word.grammar_class,
            topic=word.topic,
            example=word.example,
            author_id=user_id,
            status="approved",
        )
        db.add(db_word)
        db.commit()
        db.refresh(db_word)
        return db_word
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {e}")


# -------------------------
# GET WORDS (TRUE A–Z ORDER FIX)
# -------------------------
def get_words(db: Session, skip: int = 0, limit: int = 10):
    return (
        db.query(models.Word)
        .order_by(func.lower(models.Word.word).asc())  # ⭐ FIXED GLOBAL ORDER
        .offset(skip)
        .limit(limit)
        .all()
    )


# READ ONE (case-insensitive)
def get_word_by_name(db: Session, word_str: str):
    return (
        db.query(models.Word)
        .filter(func.lower(models.Word.word) == word_str.lower())
        .first()
    )


# READ ALL BY FIRST LETTER
def get_words_by_first_letter(db: Session, letter: str):
    if len(letter) != 1:
        return []  # only one character allowed
    return (
        db.query(models.Word)
        .filter(func.lower(models.Word.word).like(f"{letter.lower()}%"))
        .all()
    )


# UPDATE (only editable fields)
def update_word_fields(db: Session, word_str: str, word_data: dict):
    db_word = (
        db.query(models.Word)
        .filter(func.lower(models.Word.word) == word_str.lower())
        .first()
    )
    if not db_word:
        return None
    # only update allowed fields
    allowed = ["definition", "grammar_class", "topic", "example"]
    for field in allowed:
        if field in word_data:
            setattr(db_word, field, word_data[field])
    db.commit()
    db.refresh(db_word)
    return db_word


# DELETE by word (case-insensitive)
def delete_word_by_name(db: Session, word_str: str):
    db_word = (
        db.query(models.Word)
        .filter(func.lower(models.Word.word) == word_str.lower())
        .first()
    )
    if not db_word:
        return None
    db.delete(db_word)
    db.commit()
    return db_word


# DELETE ALL WORDS (debug utility)
def delete_all_words(db: Session):
    """
    Delete all words from the database
    """
    deleted_count = db.query(models.Word).delete(synchronize_session=False)
    db.commit()
    return deleted_count


def reset_test_data(db):
    import json
    from pathlib import Path
    from datetime import datetime
    from . import models

    # Path to JSON file
    file_path = Path(__file__).parent / "test_data.json"

    # Load JSON data
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Clear old data
    db.query(models.Word).delete()

    # Add new data
    for w in data:
        # Convert created_at string to datetime
        if isinstance(w.get("created_at"), str):
            w["created_at"] = datetime.fromisoformat(
                w["created_at"].replace("Z", "+00:00")
            )
        db.add(models.Word(**w))

    db.commit()
    return len(data)
