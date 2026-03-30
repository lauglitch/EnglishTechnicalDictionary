# app/words.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import crud, schemas, models

router = APIRouter(prefix="/words")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/", response_model=schemas.Word)
def create_word(word: schemas.WordCreate, db: Session = Depends(get_db)):
    new_word = crud.create_word(db, word, user_id=1)
    if new_word is None:
        raise HTTPException(status_code=400, detail="Word already exists")
    return new_word


@router.get("/", response_model=list[schemas.Word])
def read_words(status: str = None, db: Session = Depends(get_db)):
    words = crud.get_words(db, status)
    return words
