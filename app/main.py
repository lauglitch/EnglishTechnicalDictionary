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


@app.middleware("http")
async def debug_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Debug-CORS"] = "active"
    return response


# CORS configuration (for Vercel frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://english-technical-dictionary.vercel.app",
        "https://english-technical-dictionary-72p5ds41i-lauglitchs-projects.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def debug_middleware(request, call_next):
    response = await call_next(request)
    response.headers["X-Debug"] = "CORS_TEST"
    return response


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


def verify_admin(x_admin_key: str = Header(None)):
    print("HEADER RECEIVED:", x_admin_key)
    print("EXPECTED:", os.getenv("ADMIN_SECRET"))

    if x_admin_key != os.getenv("ADMIN_SECRET"):
        raise HTTPException(status_code=403, detail="Unauthorized")
