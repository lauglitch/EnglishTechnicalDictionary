# app/crud.py
from sqlalchemy.orm import Session
from app import models, schemas


def create_word(db: Session, word: schemas.WordCreate, user_id: int):
    # check duplicate (case-insensitive)
    existing = db.query(models.Word).filter(models.Word.word.ilike(word.word)).first()
    if existing:
        return None  # already exists
    db_word = models.Word(
        word=word.word,
        definition=word.definition,
        grammar_class=word.grammar_class,
        topic=word.topic,
        example=word.example,
        author_id=user_id,
        status="approved",  # approved by default for testing
    )
    db.add(db_word)
    db.commit()
    db.refresh(db_word)
    return db_word


def get_words(db: Session, status: str = None):
    if status:
        return db.query(models.Word).filter(models.Word.status == status).all()
    return db.query(models.Word).all()
