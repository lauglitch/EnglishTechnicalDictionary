from sqlalchemy.orm import Session
from sqlalchemy import func
from app import models, schemas
from pathlib import Path
import json
from fastapi import HTTPException


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


# READ ALL
def get_words(db: Session, skip: int = 0, limit: int = 50):
    return db.query(models.Word).offset(skip).limit(limit).all()


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


def reset_test_data(db: Session):
    """
    Delete all words and insert test data from test_data.json
    """
    db.query(models.Word).delete(synchronize_session=False)
    db.commit()

    json_path = Path(__file__).parent / "test_data.json"
    with open(json_path, "r", encoding="utf-8") as f:
        test_words = json.load(f)

    for w in test_words:
        db.add(models.Word(**w))
    db.commit()
    return len(test_words)
