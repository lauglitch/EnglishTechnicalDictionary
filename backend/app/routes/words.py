# app/words.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List

from app import crud, schemas, models
from app.database import SessionLocal

router = APIRouter(prefix="/words", tags=["words"])


# -------------------------
# DB SESSION
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# DEBUG ROUTES
# -------------------------
@router.delete("/all")
def delete_all_words_route(db: Session = Depends(get_db)):
    deleted_count = crud.delete_all_words(db)
    return {"deleted": deleted_count}


@router.put("/reset-test-data")
def reset_test_words(db: Session = Depends(get_db)):
    count = crud.reset_test_data(db)
    return {"reset_count": count}


# -------------------------
# GET ALL WORDS (PAGINATED)
# -------------------------
@router.get("/")
def get_all_words(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(models.Word)

    total = query.count()

    items = query.order_by(models.Word.word.asc()).offset(skip).limit(limit).all()

    return {"items": items, "total": total}


# -------------------------
# GET BY LETTER
# -------------------------
@router.get("/letter/{letter}")
def get_words_by_letter(
    letter: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    if len(letter) != 1:
        raise HTTPException(status_code=400, detail="Only one letter allowed")

    query = db.query(models.Word).filter(
        func.lower(models.Word.word).startswith(letter.lower())
    )

    total = query.count()

    items = query.order_by(models.Word.word.asc()).offset(skip).limit(limit).all()

    return {"items": items, "total": total}


# -------------------------
# GET SINGLE WORD
# -------------------------
@router.get("/{word_str}", response_model=schemas.Word)
def get_word(word_str: str, db: Session = Depends(get_db)):
    word = crud.get_word_by_name(db, word_str)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return word


# -------------------------
# CREATE WORD
# -------------------------
@router.post("/", response_model=schemas.Word)
def create_word(word: schemas.WordCreate, db: Session = Depends(get_db)):
    created = crud.create_word(db, word, user_id=1)
    if not created:
        raise HTTPException(status_code=400, detail="Word already exists")
    return created


# -------------------------
# UPDATE WORD
# -------------------------
@router.patch("/{word_str}", response_model=schemas.Word)
def patch_word(word_str: str, word_data: dict, db: Session = Depends(get_db)):
    updated = crud.update_word_fields(db, word_str, word_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Word not found")
    return updated


# -------------------------
# DELETE WORD
# -------------------------
@router.delete("/{word_str}")
def delete_word(word_str: str, db: Session = Depends(get_db)):
    deleted = crud.delete_word_by_name(db, word_str)
    if not deleted:
        raise HTTPException(status_code=404, detail="Word not found")
    return {"deleted": True}
