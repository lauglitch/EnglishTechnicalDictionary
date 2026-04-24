from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

from app import schemas, crud, models
from app.database import SessionLocal

router = APIRouter(prefix="/words", tags=["words"])


ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip().lower()


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
# ADMIN AUTH
# -------------------------
def verify_admin(x_user_email: str = Header(None)):
    print("HEADER RECEIVED:", x_user_email)

    if not x_user_email:
        raise HTTPException(status_code=401, detail="Missing email")

    if x_user_email.strip().lower() != ADMIN_EMAIL:
        raise HTTPException(status_code=403, detail="Admins only")


# -------------------------
# PUBLIC WORDS
# -------------------------
@router.get("/")
def get_all_words(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    query = db.query(models.Word).filter(models.Word.status == "approved")

    total = query.count()
    items = query.order_by(models.Word.id.desc()).offset(skip).limit(limit).all()

    return {"items": items, "total": total}


# -------------------------
# LETTER FILTER
# -------------------------
@router.get("/letter/{letter}")
def get_words_by_letter(
    letter: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)
):
    if len(letter) != 1:
        raise HTTPException(status_code=400, detail="Only one letter allowed")

    query = db.query(models.Word).filter(
        models.Word.status == "approved",
        func.lower(models.Word.word).startswith(letter.lower()),
    )

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return {"items": items, "total": total}


# -------------------------
# CREATE WORD
# -------------------------
@router.post("/")
def create_word(word: schemas.WordCreate, db: Session = Depends(get_db)):
    created = crud.create_word(db, word, user_id=1)

    if not created:
        raise HTTPException(status_code=400, detail="Word already exists")

    return created


# -------------------------
# SUBMIT WORD
# -------------------------
@router.post("/submit")
def submit_word(word: schemas.WordCreate, db: Session = Depends(get_db)):
    new_word = crud.create_word(db, word, user_id=1)

    if not new_word:
        raise HTTPException(status_code=400, detail="Word already exists")

    new_word.status = "pending"
    db.commit()
    db.refresh(new_word)

    return new_word


# -------------------------
# UPDATE WORD
# -------------------------
@router.patch("/{word_str}")
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


# -------------------------
# ADMIN DASHBOARD
# -------------------------
@router.get("/admin")
def get_admin_words(
    status: str = "all",
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    x_user_email: str = Header(None),
):
    verify_admin(x_user_email)

    query = db.query(models.Word)

    if status != "all":
        query = query.filter(models.Word.status == status)

    total = query.count()
    items = query.order_by(models.Word.id.desc()).offset(skip).limit(limit).all()

    return {"items": items, "total": total}


# -------------------------
# UPDATE STATUS
# -------------------------
@router.patch("/admin/{word_id}/status")
def update_status(
    word_id: int,
    status: str,
    db: Session = Depends(get_db),
    x_user_email: str = Header(None),
):
    verify_admin(x_user_email)

    word = db.get(models.Word, word_id)

    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    word.status = status
    db.commit()

    return word


# -------------------------
# GET SINGLE WORD
# -------------------------
@router.get("/{word_str}")
def get_word(word_str: str, db: Session = Depends(get_db)):
    word = crud.get_word_by_name(db, word_str)

    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    return word
