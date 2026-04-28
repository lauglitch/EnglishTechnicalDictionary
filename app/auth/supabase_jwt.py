import os
import time
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException
from pydantic import BaseModel

# ENV VARS
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

if not SUPABASE_PROJECT_URL:
    raise RuntimeError("SUPABASE_PROJECT_URL is not set")

# JWKS endpoint
JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"

# Cache
_JWKS_CACHE = {"keys": None, "fetched_at": 0}
CACHE_TTL_SECONDS = 3600


class SupabaseUser(BaseModel):
    sub: str
    email: str | None = None
    role: str | None = None


def _get_jwks():
    now = time.time()

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
        if _JWKS_CACHE["keys"]:
            return _JWKS_CACHE["keys"]

        raise HTTPException(status_code=401, detail="JWKS fetch failed")


def verify_supabase_jwt(token: str) -> SupabaseUser:
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

        # ✅ Return typed user instead of raw dict
        return SupabaseUser(
            sub=payload.get("sub"),
            email=payload.get("email"),
            role=payload.get("role"),
        )

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
