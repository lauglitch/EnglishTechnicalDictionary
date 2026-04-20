# DB TABLES
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)

    word = Column(String, index=True, nullable=False)
    definition = Column(String, nullable=False)

    grammar_class = Column(String, nullable=True)
    topic = Column(String, nullable=True)

    example = Column(String, nullable=True)
    author = Column(String, default="Admin")

    status = Column(String, default="approved")

    created_at = Column(DateTime, default=datetime.utcnow)

    examples = relationship("Example", back_populates="word")


class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True)
    sentence = Column(Text, nullable=False)

    word_id = Column(Integer, ForeignKey("words.id"))
    word = relationship("Word", back_populates="examples")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True)

    word_id = Column(Integer, ForeignKey("words.id"))
    correct = Column(Boolean, default=False)
