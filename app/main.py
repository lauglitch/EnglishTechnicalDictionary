# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import engine
from app import models
from app.routes import words, users


# Create tables (only if they don't exist)
models.Base.metadata.create_all(bind=engine)


# Create FastAPI app
app = FastAPI(title="English Technical Dictionary")


# CORS configuration (for Vercel frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://english-technical-dictionary.vercel.app",
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Include routers
app.include_router(words.router)
app.include_router(users.router)


# Basic endpoints
@app.get("/")
def root():
    return {"status": "API running"}


@app.get("/ping")
@app.head("/ping")
def ping():
    return {"status": "ok"}


@app.get("/CORScheck")
def corscheck():
    return {"ok": True}


# Startup log
@app.on_event("startup")
async def startup_event():
    print("✅ FastAPI started and database ready")
