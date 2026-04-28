from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import os

from app import schemas, crud, models
from app.database import SessionLocal

from app.auth.dependencies import get_current_user
from app.auth.supabase_jwt import SupabaseUser


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
# ADMIN AUTH (JWT-based now)
# -------------------------
def verify_admin(user):
    if user.get("email") != "lauglitch@gmail.com":
        raise HTTPException(403, "Not admin")


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
# LETTER FILTER (PUBLIC)
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
# CREATE WORD (PROTECTED)
# -------------------------
@router.post("/")
def create_word(
    word: schemas.WordCreate,
    db: Session = Depends(get_db),
    user: SupabaseUser = Depends(get_current_user),
):
    created = crud.create_word(db, word, user_id=user.user_id)

    if not created:
        raise HTTPException(status_code=400, detail="Word already exists")

    return created


# -------------------------
# SUBMIT WORD (PROTECTED)
# -------------------------
@router.post("/submit")
def submit_word(
    word: schemas.WordCreate,
    db: Session = Depends(get_db),
    user: SupabaseUser = Depends(get_current_user),
):
    new_word = crud.create_word(db, word, user_id=user.user_id)

    if not new_word:
        raise HTTPException(status_code=400, detail="Word already exists")

    new_word.status = "pending"
    db.commit()
    db.refresh(new_word)

    return new_word


# -------------------------
# UPDATE WORD (PROTECTED)
# -------------------------
@router.patch("/{word_str}")
def patch_word(
    word_str: str,
    word_data: dict,
    db: Session = Depends(get_db),
    user: SupabaseUser = Depends(get_current_user),
):
    updated = crud.update_word_fields(db, word_str, word_data)

    if not updated:
        raise HTTPException(status_code=404, detail="Word not found")

    return updated


# -------------------------
# DELETE WORD (PROTECTED)
# -------------------------
@router.delete("/{word_str}")
def delete_word(
    word_str: str,
    db: Session = Depends(get_db),
    user: SupabaseUser = Depends(get_current_user),
):
    deleted = crud.delete_word_by_name(db, word_str)

    if not deleted:
        raise HTTPException(status_code=404, detail="Word not found")

    return {"deleted": True}


# -------------------------
# ADMIN DASHBOARD (PROTECTED + ADMIN)
# -------------------------
@router.get("/admin")
def get_admin_words(
    status: str = "all",
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    user: SupabaseUser = Depends(get_current_user),
):
    verify_admin(user)

    query = db.query(models.Word)

    if status != "all":
        query = query.filter(models.Word.status == status)

    total = query.count()
    items = query.order_by(models.Word.id.desc()).offset(skip).limit(limit).all()

    return {"items": items, "total": total}


# -------------------------
# UPDATE STATUS (ADMIN)
# -------------------------
@router.patch("/admin/{word_id}/status")
def update_status(
    word_id: int,
    status: str,
    db: Session = Depends(get_db),
    user: SupabaseUser = Depends(get_current_user),
):
    verify_admin(user)

    word = db.get(models.Word, word_id)

    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    word.status = status
    db.commit()

    return word


# -------------------------
# TEST PROTECTED ROUTE
# -------------------------
@router.get("/protected")
async def protected_route(user: SupabaseUser = Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user_id": user.user_id,
        "email": user["email"],
    }


# -------------------------
# GET SINGLE WORD (PUBLIC)
# -------------------------
@router.get("/{word_str}")
def get_word(word_str: str, db: Session = Depends(get_db)):
    word = crud.get_word_by_name(db, word_str)

    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    return word
