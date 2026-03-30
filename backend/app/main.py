# app/main.py
from fastapi import FastAPI
from app.database import Base, engine
from app.routes.words import router as words_router
from app import models

# create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="English Technical Dictionary")

app.include_router(words_router)

# seed initial words if DB empty
from sqlalchemy.orm import Session


def seed_words():
    db = Session(bind=engine)
    if db.query(models.Word).count() == 0:
        initial_words = [
            {
                "word": "Pipeline",
                "definition": "A sequence of data processing steps",
                "grammar_class": "noun",
                "topic": "Big Data",
                "example": "We built a pipeline for ETL",
            },
            {
                "word": "Dataset",
                "definition": "A collection of structured data",
                "grammar_class": "noun",
                "topic": "Big Data",
                "example": "The dataset contains 1 million rows",
            },
            {
                "word": "Model",
                "definition": "A mathematical representation of a system",
                "grammar_class": "noun",
                "topic": "Machine Learning",
                "example": "We trained a predictive model",
            },
            {
                "word": "Performance",
                "definition": "How well a system operates",
                "grammar_class": "noun",
                "topic": "Software",
                "example": "We measured the system performance",
            },
            {
                "word": "Accuracy",
                "definition": "The degree of correctness",
                "grammar_class": "noun",
                "topic": "Machine Learning",
                "example": "The model achieved 95% accuracy",
            },
            {
                "word": "Latency",
                "definition": "The delay before a response",
                "grammar_class": "noun",
                "topic": "Networking",
                "example": "Low latency is critical for gaming",
            },
            {
                "word": "Scalable",
                "definition": "Able to handle growth",
                "grammar_class": "adjective",
                "topic": "Software Architecture",
                "example": "The system is highly scalable",
            },
            {
                "word": "Optimize",
                "definition": "Make as effective as possible",
                "grammar_class": "verb",
                "topic": "Software Engineering",
                "example": "We optimized the database queries",
            },
        ]
        for w in initial_words:
            db.add(models.Word(**w, status="approved", author_id=1))
        db.commit()
    db.close()


seed_words()
