# main.py
from fastapi import FastAPI
from . import models
from .database import engine
from .routes import words
from fastapi.middleware.cors import CORSMiddleware

# Create all tables in the database (if they don't exist)
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="English Technical Dictionary")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include your router(s)
app.include_router(words.router)


# Optional: startup event for logging
@app.on_event("startup")
async def startup_event():
    print("✅ Database tables checked/created. FastAPI is ready.")
