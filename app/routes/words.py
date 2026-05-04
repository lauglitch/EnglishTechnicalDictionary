from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi.encoders import jsonable_encoder

from app import schemas, crud, models
from app.database import SessionLocal
from app.auth.dependencies import get_current_user

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
# ADMIN CHECK
# -------------------------
def verify_admin(user: dict):
    role = user.get("app_metadata", {}).get("role") or user.get(
        "user_metadata", {}
    ).get("role")

    if role != "admin":
        raise HTTPException(status_code=403, detail="Not admin")


# =========================================================
# PUBLIC WORDS (ONLY APPROVED)
# =========================================================
@router.get("/")
def get_all_words(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    query = db.query(models.Word).filter(models.Word.status == "approved")

    query = query.order_by(func.lower(models.Word.word).asc(), models.Word.id.asc())

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return {"items": jsonable_encoder(items), "total": total}


# =========================================================
# LETTER FILTER
# =========================================================
@router.get("/letter/{letter}")
def get_words_by_letter(
    letter: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    if len(letter) != 1:
        raise HTTPException(status_code=400, detail="Only one letter allowed")

    query = db.query(models.Word).filter(
        models.Word.status == "approved",
        func.lower(models.Word.word).startswith(letter.lower()),
    )

    query = query.order_by(func.lower(models.Word.word).asc(), models.Word.id.asc())

    total = query.count()
    items = query.offset(skip).limit(limit).all()

    return {"items": jsonable_encoder(items), "total": total}


# =========================================================
# SUBMIT WORD (USER → PENDING QUEUE)
# =========================================================
@router.post("/submit")
def submit_word(
    word: schemas.WordCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    # ❗ NO insert into Word table directly
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


# =========================================================
# ADMIN: CREATE FINAL WORD (optional manual override)
# =========================================================
@router.post("/")
def create_word(
    word: schemas.WordCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    verify_admin(user)

    return crud.create_word(db, word, user_id=user.get("sub"))


# =========================================================
# ADMIN: UPDATE WORD
# =========================================================
@router.patch("/{word_str}")
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


# =========================================================
# ADMIN: DELETE WORD
# =========================================================
@router.delete("/{word_str}")
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


# =========================================================
# ADMIN: STATUS UPDATE (APPROVE / REJECT)
# =========================================================
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


# =========================================================
# GET SINGLE WORD (ONLY APPROVED)
# =========================================================
@router.get("/{word_str}")
def get_word(word_str: str, db: Session = Depends(get_db)):
    word = crud.get_word_by_name(db, word_str)

    if not word or word.status != "approved":
        raise HTTPException(status_code=404, detail="Word not found")

    return word


# =========================================================
# ADMIN DEBUG (optional)
# =========================================================
@router.get("/admin/debug")
def admin_debug(user=Depends(get_current_user)):
    verify_admin(user)

    return {
        "email": user.get("email"),
        "role": user.get("app_metadata", {}).get("role"),
    }
