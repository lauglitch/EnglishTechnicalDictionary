# app/main.py

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

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://english-technical-dictionary.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def debug_middleware(request, call_next):
    print("➡️ REQUEST PATH:", request.url.path)
    print("➡️ HEADERS:", dict(request.headers))

    response = await call_next(request)

    response.headers["X-Debug"] = "CORS_OK"
    return response


# Include routers ONLY ONCE
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


def verify_admin(x_user_email: str = Header(None)):
    print("HEADER RECEIVED:", x_user_email)
    print("EXPECTED:", os.getenv("ADMIN_EMAIL"))

    if not x_user_email:
        raise HTTPException(status_code=401, detail="Missing email")

    if x_user_email.lower() != os.getenv("ADMIN_EMAIL", "").lower():
        raise HTTPException(status_code=403, detail="Admins only")
