# app/words.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app import crud, schemas
from app.database import SessionLocal

router = APIRouter(prefix="/words", tags=["words"])


# -------------------------
# Dependency to get DB session
# -------------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# -------------------------
# DEBUG ROUTES (must come first!)
# -------------------------


# DELETE ALL (debug only)
@router.delete("/all", summary="Delete all words (debug only)")
def delete_all_words_route(db: Session = Depends(get_db)):
    deleted_count = crud.delete_all_words(db)
    return {"deleted": deleted_count}


# RESET test data from JSON (debug only)
@router.put("/reset-test-data", summary="Reset DB with test words (debug only)")
def reset_test_words(db: Session = Depends(get_db)):
    count = crud.reset_test_data(db)  # Reads from JSON
    return {"reset_count": count}


# -------------------------
# CRUD ROUTES
# -------------------------


# GET all words
@router.get("/", response_model=List[schemas.Word])
def get_all_words(
    skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):  # gets 50 words
    return crud.get_words(db, skip=skip, limit=limit)


# GET words by first letter (single character only)
@router.get("/letter/{letter}", response_model=List[schemas.Word])
def get_words_by_letter(letter: str, db: Session = Depends(get_db)):
    if len(letter) != 1:
        raise HTTPException(status_code=400, detail="Only one letter allowed")
    return crud.get_words_by_first_letter(db, letter)


# GET single word (case-insensitive)
@router.get("/{word_str}", response_model=schemas.Word)
def get_word(word_str: str, db: Session = Depends(get_db)):
    word = crud.get_word_by_name(db, word_str)
    if not word:
        raise HTTPException(status_code=404, detail="Word not found")
    return word


# POST new word
@router.post("/", response_model=schemas.Word)
def create_word(
    word: schemas.WordCreate, db: Session = Depends(get_db), user_id: int = 1
):
    created = crud.create_word(db, word, user_id)
    if not created:
        raise HTTPException(status_code=400, detail="Word already exists")
    return created


# PATCH single word (partial update)
@router.patch("/{word_str}", response_model=schemas.Word)
def patch_word(word_str: str, word_data: dict, db: Session = Depends(get_db)):
    updated = crud.update_word_fields(db, word_str, word_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Word not found")
    return updated


# DELETE single word by name
@router.delete("/{word_str}", summary="Delete a word by name")
def delete_word(word_str: str, db: Session = Depends(get_db)):
    deleted = crud.delete_word_by_name(db, word_str)
    if not deleted:
        raise HTTPException(status_code=404, detail="Word not found")
    return {"deleted": True}
