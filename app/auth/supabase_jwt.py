import os
import time
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException
from typing import TypedDict, Optional


# -----------------------------
# SUPABASE USER TYPE (FIX)
# -----------------------------
class SupabaseUser(TypedDict, total=False):
    sub: str
    email: Optional[str]
    role: Optional[str]
    aud: Optional[str]


SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

if not SUPABASE_PROJECT_URL:
    raise RuntimeError("SUPABASE_PROJECT_URL is not set in environment variables")

JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"

_JWKS_CACHE = {"keys": None, "fetched_at": 0}
CACHE_TTL_SECONDS = 3600


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

        raise HTTPException(
            status_code=401,
            detail="Auth service unavailable (JWKS fetch failed)",
        )


# -----------------------------
# JWT VERIFY (returns SupabaseUser)
# -----------------------------
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
            algorithms=["RS256"],
            audience="authenticated",
            issuer=f"{SUPABASE_PROJECT_URL}/auth/v1",
        )

        # normalize into SupabaseUser shape
        return {
            "sub": payload.get("sub"),
            "email": payload.get("email"),
            "role": payload.get("role"),
            "aud": payload.get("aud"),
        }

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Token verification failed: {str(e)}",
        )
