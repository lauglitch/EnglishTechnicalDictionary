# DB TABLES
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True, nullable=False, index=True)
    definition = Column(Text, nullable=False)

    category_id = Column(Integer, ForeignKey("categories.id"))
    difficulty = Column(Integer, default=1)

    category = relationship("Category")
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
