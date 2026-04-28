# app/main.py
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os

from app.database import engine
from app import models
from app.routes import words, users


# Create tables (only if they don't exist)
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(title="English Technical Dictionary")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://english-technical-dictionary.vercel.app",
        "https://english-technical-dictionary-git-staging-lauglitchs-projects.vercel.app",
    ],
    allow_origin_regex=r"https://.*vercel\.app$",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def debug_middleware(request, call_next):
    print("REQUEST PATH:", request.url.path)
    print("HEADERS:", dict(request.headers))

    response = await call_next(request)

    response.headers["X-Debug"] = "CORS_OK"
    return response


# Include routers ONLY ONCE
app.include_router(words.router)
app.include_router(users.router)

SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

print("SECRET LOADED:", SUPABASE_JWT_SECRET is not None)


@app.get("/test")
def test():
    return {"ok": True}


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
