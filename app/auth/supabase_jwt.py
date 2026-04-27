import os
import httpx
from jose import jwt
from fastapi import HTTPException, status
from functools import lru_cache

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"


class SupabaseUser:
    def __init__(self, user_id: str, email: str = None, raw: dict = None):
        self.user_id = user_id
        self.email = email
        self.raw = raw or {}


# -------------------------
# CACHE JWKS (IMPORTANT)
# -------------------------
@lru_cache(maxsize=1)
def get_jwks():
    try:
        with httpx.Client(timeout=5.0) as client:
            return client.get(JWKS_URL).json()
    except Exception as e:
        raise HTTPException(
            status_code=503, detail="Auth service unavailable (JWKS fetch failed)"
        ) from e


# -------------------------
# VERIFY TOKEN
# -------------------------
async def verify_supabase_jwt(token: str) -> SupabaseUser:
    try:
        jwks = get_jwks()

        header = jwt.get_unverified_header(token)
        kid = header.get("kid")

        key = next((k for k in jwks["keys"] if k["kid"] == kid), None)

        if not key:
            raise HTTPException(
                status_code=401, detail="Invalid token key (kid not found)"
            )

        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=f"{SUPABASE_PROJECT_URL}/auth/v1",
            options={
                "verify_signature": True,
                "verify_aud": True,
                "verify_exp": True,
            },
        )

        return SupabaseUser(
            user_id=payload.get("sub"),
            email=payload.get("email"),
            raw=payload,
        )

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.JWTError as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(status_code=401, detail="Authentication failed")
