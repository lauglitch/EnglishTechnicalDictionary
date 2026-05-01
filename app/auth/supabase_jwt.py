import os
import time
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException
from typing import TypedDict, Optional


# -----------------------------
# SUPABASE USER TYPE
# -----------------------------
class SupabaseUser(TypedDict, total=False):
    sub: str
    email: Optional[str]
    role: Optional[str]
    aud: Optional[str]


# -----------------------------
# ENV
# -----------------------------
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")

if not SUPABASE_PROJECT_URL:
    raise RuntimeError("SUPABASE_PROJECT_URL is not set in environment variables")

JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"


# -----------------------------
# JWKS CACHE
# -----------------------------
_JWKS_CACHE = {
    "keys": None,
    "fetched_at": 0,
}

CACHE_TTL_SECONDS = 3600


# -----------------------------
# FETCH JWKS (with cache)
# -----------------------------
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
        # fallback to cached keys if available
        if _JWKS_CACHE["keys"]:
            return _JWKS_CACHE["keys"]

        raise HTTPException(
            status_code=401,
            detail="Auth service unavailable (JWKS fetch failed)",
        )


# -----------------------------
# VERIFY JWT (ES256 - Supabase)
# -----------------------------
def verify_supabase_jwt(token: str) -> SupabaseUser:
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        jwks = _get_jwks()

        # read token header
        headers = jwt.get_unverified_header(token)
        kid = headers.get("kid")

        if not kid:
            raise HTTPException(status_code=401, detail="Invalid token header")

        # find matching key
        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)

        if not key:
            raise HTTPException(status_code=401, detail="Public key not found")

        # decode token (IMPORTANT: ES256, no manual key conversion)
        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=f"{SUPABASE_PROJECT_URL}/auth/v1",
        )

        # print("JWT HEADER:", headers)
        # print("JWT PAYLOAD:", payload)

        return {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "aud": payload.get("aud"),
        }

    except JWTError as e:
        print("JWT ERROR:", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        print("JWT VERIFY FAIL:", str(e))
        raise HTTPException(
            status_code=401,
            detail=f"Token verification failed: {str(e)}",
        )
