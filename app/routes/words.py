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
    role = user.get("app_metadata", {}).get("role")

    if role != "admin":
        raise HTTPException(status_code=403, detail="Not admin")


# -------------------------
# ADMIN WORDS
# -------------------------
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

    # CRITICAL: stable global order
    query = query.order_by(func.lower(models.Word.word).asc(), models.Word.id.asc())

    total = query.count()

    items = query.offset(skip).limit(limit).all()

    return {
        "items": jsonable_encoder(items),
        "total": total,
    }


# -------------------------
# PUBLIC WORDS
# -------------------------
@router.get("/")
def get_all_words(
    skip: int = 0,
    limit: int = 10,
    status: str = "approved",
    db: Session = Depends(get_db),
):
    query = db.query(models.Word)

    if status != "all":
        query = query.filter(models.Word.status == status)

    query = query.order_by(func.lower(models.Word.word).asc(), models.Word.id.asc())

    total = query.count()

    items = query.offset(skip).limit(limit).all()

    return {
        "items": jsonable_encoder(items),
        "total": total,
    }


# -------------------------
# LETTER FILTER
# -------------------------
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

    return {
        "items": jsonable_encoder(items),
        "total": total,
    }


# -------------------------
# CREATE WORD
# -------------------------
@router.post("/")
def create_word(
    word: schemas.WordCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    verify_admin(user)
    return crud.create_word(db, word, user_id=user.get("sub"))


# -------------------------
# SUBMIT WORD
# -------------------------
@router.post("/submit")
def submit_word(
    word: schemas.WordCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    verify_admin(user)
    new_word = crud.create_word(db, word, user_id=user.get("sub"))

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
def patch_word(
    word_str: str,
    word_data: schemas.WordUpdate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    verify_admin(user)
    updated = crud.update_word_fields(db, word_str, word_data.dict(exclude_unset=True))

    if not updated:
        raise HTTPException(status_code=404, detail="Word not found")

    return updated


# -------------------------
# DELETE WORD
# -------------------------
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


# -------------------------
# ADMIN DEBUG ROUTE
# -------------------------
@router.get("/admin")
def admin_route(user=Depends(get_current_user)):
    verify_admin(user)

    return {
        "message": "Admin access granted",
        "email": user.get("email"),
        "role": user.get("app_metadata", {}).get("role"),
    }


# -------------------------
# UPDATE STATUS (ADMIN)
# -------------------------
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


# -------------------------
# PROTECTED TEST ROUTE
# -------------------------
@router.get("/protected")
def protected_route(user=Depends(get_current_user)):
    return {
        "message": "You are authenticated",
        "user_id": user.get("sub"),
        "email": user.get("email"),
    }


# -------------------------
# GET SINGLE WORD
# -------------------------
@router.get("/{word_str}")
def get_word(word_str: str, db: Session = Depends(get_db)):
    word = crud.get_word_by_name(db, word_str)

    if not word:
        raise HTTPException(status_code=404, detail="Word not found")

    return word
