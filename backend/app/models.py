# DB TABLES
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from backend.app.database import Base


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)


class Vocabulary(Base):
    __tablename__ = "vocabulary"

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

    word_id = Column(Integer, ForeignKey("vocabulary.id"))
    word = relationship("Vocabulary", back_populates="examples")


class UserProgress(Base):
    __tablename__ = "user_progress"

    id = Column(Integer, primary_key=True)

    word_id = Column(Integer, ForeignKey("vocabulary.id"))
    correct = Column(Boolean, default=False)
