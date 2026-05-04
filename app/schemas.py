from pydantic import BaseModel, Field, validator
from typing import Optional
from app.database import Base


# -------------------------
# BASE
# -------------------------
class WordBase(BaseModel):
    word: str
    definition: str
    grammar_class: Optional[str] = None
    topic: Optional[str] = None
    example: Optional[str] = None


# -------------------------
# CREATE WORD
# -------------------------
class WordCreate(BaseModel):
    word: str = Field(..., min_length=1)
    definition: str = Field(..., min_length=1)
    grammar_class: Optional[str] = None
    topic: Optional[str] = None
    example: Optional[str] = None

    @validator("grammar_class")
    def valid_grammar_class(cls, v):
        allowed = ["noun", "verb", "adjective", "adverb", None]
        if v not in allowed:
            raise ValueError(f"grammar_class must be one of {allowed}")
        return v


# -------------------------
# UPDATE WORD
# -------------------------
class WordUpdate(BaseModel):
    word: Optional[str] = None
    definition: Optional[str] = None
    grammar_class: Optional[str] = None
    topic: Optional[str] = None
    example: Optional[str] = None

    @validator("grammar_class")
    def valid_grammar_class(cls, v):
        allowed = ["noun", "verb", "adjective", "adverb", None]
        if v not in allowed:
            raise ValueError(f"grammar_class must be one of {allowed}")
        return v


# -------------------------
# RESPONSE MODEL
# -------------------------
class Word(WordBase):
    id: int
    author: str
    status: str

    class Config:
        from_attributes = True
