from pydantic import BaseModel, Field, validator
from typing import Optional


class WordBase(BaseModel):
    word: str
    definition: str
    grammar_class: Optional[str] = None
    topic: Optional[str] = None
    example: Optional[str] = None


# Used when creating a new word
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


# Used in responses (includes id, author, status)
class Word(WordBase):
    id: int
    author: str
    status: str

    class Config:
        orm_mode = True
