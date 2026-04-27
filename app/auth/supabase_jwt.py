import os
import time
import requests
from jose import jwt, JWTError
from fastapi import HTTPException

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL is not set in environment variables")

# JWKS endpoint (Supabase public keys)
JWKS_URL = f"{SUPABASE_URL}/auth/v1/.well-known/jwks.json"

# Cache JWKS in memory (important for Render stability)
_JWKS_CACHE = {"keys": None, "fetched_at": 0}

CACHE_TTL_SECONDS = 3600  # 1 hour


def _get_jwks():
    """
    Fetch JWKS with caching to avoid Render network instability.
    """
    now = time.time()

    # return cached version if still valid
    if _JWKS_CACHE["keys"] and (now - _JWKS_CACHE["fetched_at"] < CACHE_TTL_SECONDS):
        return _JWKS_CACHE["keys"]

    try:
        response = requests.get(JWKS_URL, timeout=5)
        response.raise_for_status()
        jwks = response.json()

        _JWKS_CACHE["keys"] = jwks
        _JWKS_CACHE["fetched_at"] = now

        return jwks

    except Exception as e:
        # IMPORTANT: do NOT crash app with 503
        # fallback to cached keys if available
        if _JWKS_CACHE["keys"]:
            return _JWKS_CACHE["keys"]

        raise HTTPException(
            status_code=401,
            detail=f"Auth service unavailable (JWKS fetch failed): {str(e)}",
        )


def verify_supabase_jwt(token: str):
    """
    Verify Supabase JWT in a production-safe way.
    Never throws 503 anymore.
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
            issuer=f"{SUPABASE_URL}/auth/v1",
        )

        return payload

    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        # IMPORTANT: never leak 500/503 to frontend for auth
        raise HTTPException(
            status_code=401, detail=f"Token verification failed: {str(e)}"
        )
