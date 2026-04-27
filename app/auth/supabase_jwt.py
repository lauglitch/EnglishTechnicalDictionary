import os
import time
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException

# ENV VAR (your requested naming)
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

if not SUPABASE_PROJECT_URL:
    raise RuntimeError("SUPABASE_PROJECT_URL is not set in environment variables")

# Supabase JWKS endpoint
JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"

# Cache JWKS to avoid repeated network calls (important for Render stability)
_JWKS_CACHE = {"keys": None, "fetched_at": 0}

CACHE_TTL_SECONDS = 3600  # 1 hour cache


def _get_jwks():
    """
    Fetch JWKS with caching and fallback.
    Prevents Render cold-start / network issues from breaking auth.
    """
    now = time.time()

    # return cached keys if still valid
    if _JWKS_CACHE["keys"] and (now - _JWKS_CACHE["fetched_at"] < CACHE_TTL_SECONDS):
        return _JWKS_CACHE["keys"]

    try:
        with httpx.Client(timeout=5) as client:
            response = client.get(JWKS_URL)
            response.raise_for_status()
            jwks = response.json()

        _JWKS_CACHE["keys"] = jwks
        _JWKS_CACHE["fetched_at"] = now

        return jwks

    except Exception:
        # fallback: use cache if available
        if _JWKS_CACHE["keys"]:
            return _JWKS_CACHE["keys"]

        raise HTTPException(
            status_code=401, detail="Auth service unavailable (JWKS fetch failed)"
        )


def verify_supabase_jwt(token: str):
    """
    Verifies Supabase JWT safely (production-ready).
    Never breaks CORS or crashes server.
    """

    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        jwks = _get_jwks()

        headers = jwt.get_unverified_header(token)
        kid = headers.get("kid")

        if not kid:
            raise HTTPException(status_code=401, detail="Invalid token header")

        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)

        if not key:
            raise HTTPException(status_code=401, detail="Public key not found")

        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=f"{SUPABASE_PROJECT_URL}/auth/v1",
        )

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        raise HTTPException(
            status_code=401, detail=f"Token verification failed: {str(e)}"
        )
