import os
import httpx
from jose import jwt
from fastapi import HTTPException, status, Request

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")

JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"


class SupabaseUser:
    def __init__(self, user_id: str, email: str = None, raw: dict = None):
        self.user_id = user_id
        self.email = email
        self.raw = raw or {}


async def verify_supabase_jwt(token: str) -> SupabaseUser:
    """
    Validates Supabase JWT using JWKS (ES256 compatible)
    """

    try:
        # 1. Fetch Supabase public keys
        async with httpx.AsyncClient() as client:
            jwks = (await client.get(JWKS_URL)).json()

        # 2. Read token header (to get key id)
        unverified_header = jwt.get_unverified_header(token)

        # 3. Find correct key
        key = next(
            (k for k in jwks["keys"] if k["kid"] == unverified_header["kid"]), None
        )

        if not key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token key",
            )

        # 4. Verify JWT
        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=f"{SUPABASE_PROJECT_URL}/auth/v1",
        )

        # 5. Extract user info
        user_id = payload.get("sub")
        email = payload.get("email")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user id",
            )

        return SupabaseUser(user_id=user_id, email=email, raw=payload)

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_token_from_header(request: Request) -> str:
    auth = request.headers.get("Authorization")

    if not auth:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header",
        )

    scheme, _, token = auth.partition(" ")

    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format",
        )

    return token
