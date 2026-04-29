from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt
import requests
import os

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")

SUPABASE_ISSUER = f"{SUPABASE_PROJECT_URL}/auth/v1"

JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"

security = HTTPBearer()


def get_jwks():
    try:
        r = requests.get(JWKS_URL, timeout=10)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print("JWKS fetch error:", e)
        raise HTTPException(status_code=500, detail="Cannot fetch JWKS")


JWKS = get_jwks()


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials

    try:
        headers = jwt.get_unverified_header(token)
        kid = headers.get("kid")

        if not kid:
            raise HTTPException(status_code=401, detail="Missing kid in token")

        key = next((k for k in JWKS.get("keys", []) if k.get("kid") == kid), None)

        if not key:
            raise HTTPException(status_code=401, detail="JWKS key not found")

        payload = jwt.decode(
            token,
            key,
            algorithms=["ES256"],
            audience="authenticated",
            issuer=SUPABASE_ISSUER,
        )

        return payload

    except Exception as e:
        print("JWT ERROR:", str(e))
        raise HTTPException(status_code=401, detail="Token verification failed")
