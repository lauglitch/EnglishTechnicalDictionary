from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)
    word = Column(String, unique=True, index=True, nullable=False)
    definition = Column(String, nullable=False)
    grammar_class = Column(String, nullable=True)
    topic = Column(String, nullable=True)
    example = Column(String, nullable=True)
    status = Column(String, default="pending")  # pending | approved | rejected
    author = Column(String, nullable=False, default="Admin")
    created_at = Column(DateTime, default=datetime.utcnow)
