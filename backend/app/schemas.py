# app/schemas.py
from pydantic import BaseModel


class WordBase(BaseModel):
    word: str
    definition: str
    grammar_class: str
    topic: str
    example: str


class WordCreate(WordBase):
    pass


class Word(WordBase):
    id: int
    status: str
    author_id: int

    class Config:
        orm_mode = True
