from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.encoders import jsonable_encoder

from app import schemas, crud, models
from app.database import SessionLocal
from app.auth.dependencies import get_current_user
from app.auth.permissions import verify_admin

router = APIRouter(prefix="/words", tags=["words"])


# =========================
# DB
# =========================
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# PUBLIC (approved only)
# =========================
@router.get("/")
def get_all_words(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):

    query = (
        db.query(models.Word)
        .filter(models.Word.status == "approved")
        .order_by(func.lower(models.Word.word), models.Word.id)
    )

    items = query.offset(skip).limit(limit).all()

    return {
        "items": jsonable_encoder(items),
        "total": query.count(),
    }


@router.get("/letter/{letter}")
def get_words_by_letter(letter: str, db: Session = Depends(get_db)):

    if len(letter) != 1:
        raise HTTPException(status_code=400, detail="Only one letter allowed")

    query = (
        db.query(models.Word)
        .filter(
            models.Word.status == "approved",
            func.lower(models.Word.word).startswith(letter.lower()),
        )
        .order_by(func.lower(models.Word.word), models.Word.id)
    )

    return {
        "items": jsonable_encoder(query.all()),
        "total": query.count(),
    }


@router.get("/{word_str}")
def get_word(word_str: str, db: Session = Depends(get_db)):

    word = (
        db.query(models.Word)
        .filter(
            func.lower(models.Word.word) == word_str.lower(),
            models.Word.status == "approved",
        )
        .first()
    )

    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    return word


# =========================
# USER (submit only)
# =========================
@router.post("/submit")
def submit_word(
    word: schemas.WordCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    submission = crud.create_word_submission(
        db,
        word,
        user_id=user.get("sub"),
    )

    if not submission:
        raise HTTPException(status_code=400, detail="Word already exists")

    return {
        "message": "Submitted for review",
        "status": "pending",
    }


# =========================
# ADMIN LIST
# =========================
@router.get("/admin")
def get_admin_words(
    skip: int = 0,
    limit: int = 10,
    status: str = "all",
    user=Depends(get_current_user),
    db: Session = Depends(get_db),
):

    verify_admin(user)

    query = db.query(models.Word)

    if status != "all":
        query = query.filter(models.Word.status == status)

    query = query.order_by(func.lower(models.Word.word), models.Word.id)

    return {
        "items": jsonable_encoder(query.offset(skip).limit(limit).all()),
        "total": query.count(),
    }


# =========================
# ADMIN CREATE
# =========================
@router.post("/")
def create_word(
    word: schemas.WordCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    verify_admin(user)

    return crud.create_word(db, word, user_id=user.get("sub"))


# =========================
# ADMIN UPDATE
# =========================
@router.patch("/admin/{word_str}")
def patch_word(
    word_str: str,
    word_data: schemas.WordUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    verify_admin(user)

    updated = crud.update_word_fields(
        db,
        word_str,
        word_data.dict(exclude_unset=True),
    )

    if not updated:
        raise HTTPException(status_code=404, detail="Word not found")

    return updated


# =========================
# ADMIN DELETE
# =========================
@router.delete("/admin/{word_str}")
def delete_word(
    word_str: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    verify_admin(user)

    deleted = crud.delete_word_by_name(db, word_str)

    if not deleted:
        raise HTTPException(status_code=404, detail="Word not found")

    return {"deleted": True}


# =========================
# ADMIN STATUS UPDATE
# =========================
@router.patch("/admin/{word_id}/status")
def update_status(
    word_id: int,
    status: str,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):

    verify_admin(user)

    word = db.get(models.Word, word_id)

    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    word.status = status
    db.commit()

    return word


# =========================
# ADMIN DEBUG
# =========================
@router.get("/admin/debug")
def admin_debug(user=Depends(get_current_user)):

    verify_admin(user)

    return {
        "email": user.get("email"),
        "role": user.get("app_metadata", {}).get("role"),
    }
