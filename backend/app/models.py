# app/models.py
from sqlalchemy import Column, Integer, String
from app.database import Base


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True, nullable=False)
    definition = Column(String, nullable=False)
    grammar_class = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    example = Column(String, nullable=False)
    status = Column(String, default="pending")  # pending / approved
    author_id = Column(Integer, default=1)  # simple owner
