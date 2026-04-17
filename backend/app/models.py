from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from .database import Base


class Word(Base):
    __tablename__ = "words"

    id = Column(Integer, primary_key=True, index=True)

    word = Column(String, unique=True, index=True, nullable=False)
    definition = Column(String, nullable=False)
    example = Column(String, nullable=True)
    topic = Column(String, nullable=True)

    grammar_class = Column(String, nullable=True)

    author_id = Column(Integer, nullable=True)

    status = Column(String, default="pending")

    # AI
    ai_score = Column(Float, nullable=True)
    ai_flags = Column(String, nullable=True)
    ai_approved = Column(Boolean, default=False)

    # moderation lifecycle
    created_at = Column(DateTime, nullable=True)
