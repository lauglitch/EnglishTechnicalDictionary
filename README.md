# Technical Dictionary (Full Stack Project)

## Overview

Full-stack technical dictionary application built with:

- Backend: FastAPI + SQLAlchemy + PostgreSQL (Supabase)
- Frontend: React (Vite)
- Deployment: Render (backend) + Vercel (frontend)

Features:
- Word browsing
- Search system
- Pagination
- Alphabet filtering
- Card / Book UI modes
- Dark mode
- Environment-based configuration

---

## Architecture

### Backend
- FastAPI REST API
- PostgreSQL (Supabase)
- SQLAlchemy ORM
- Modular structure:
  - models.py
  - schemas.py
  - crud.py
  - routes

### Frontend
- React + Vite
- Axios for API calls
- State-based UI
- Pagination + filters

---

## Environment Variables

### Backend (.env)

```env
DATABASE_URL=my_postgres_connection_url
```

---

### Frontend (.env)

```env
VITE_API_URL=my_backend_url/words
```

---

## Running Locally

### Backend

```bash
uvicorn app.main:app --reload
```

### Frontend

```bash
npm install
npm run dev
```

---

## Deployment

### Render (Backend)

Build command:

```bash
pip install -r requirements.txt
```

Start command:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 10000
```

---

### Vercel (Frontend)

Set environment variable:

```env
VITE_API_URL=https://my-backend-url/words
```

---

## API Endpoints

### Get words (pagination)

```http
GET /words/?skip=0&limit=3
```

Response:

```json
{
  "items": [],
  "total": 25
}
```

---

### Search word

```http
GET /words/{word}
```

Example:

```http
GET /words/algorithm
```

---

### Filter by letter

```http
GET /words/letter/a?skip=0&limit=3
```

---

## Key Fixes Implemented

### 1. Pagination fix
Backend now returns total count:

```python
return {
    "items": items,
    "total": total
}
```

Frontend uses:

```javascript
const hasMore = (page + 1) * PAGE_SIZE < total;
```

---

### 2. CORS fix

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "https://vercel-domain.vercel.app"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

### 3. Environment variable fix

Frontend API switching:

```javascript
const API =
  import.meta.env.VITE_API_URL ||
  "http://localhost:8000/words";
```

---

### 4. Supabase migration

Replaced JSON storage with PostgreSQL database.

Seed script used to populate initial dataset.

---

### 5. Deployment issues resolved

- Render CORS blocking requests
- Vercel cache confusion
- API mismatch between local and production
- Missing environment variables

---

## Current System Flow

1. React frontend (Vercel)
2. Axios requests to backend
3. FastAPI backend (Render)
4. PostgreSQL (Supabase)
5. Response returned to UI

---

## Future Improvements

- Admin dashboard for managing words
- AI moderation system for submissions
- User authentication system
- Word contribution system
- Better UI/UX improvements

---

## Summary

The project evolved from a local JSON dictionary into a full production system with:

- Cloud database (Supabase)
- REST API backend (FastAPI)
- Modern frontend (React + Vite)
- Deployment pipeline (Render + Vercel)
- Pagination + filtering system
```
