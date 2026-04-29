import requests
from jose import jwt
from fastapi import HTTPException
import os

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")

JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"
ISSUER = f"{SUPABASE_PROJECT_URL}/auth/v1"
ALGORITHMS = ["ES256"]

# cache JWKS (important for performance)
_jwks_cache = None


def get_jwks():
    global _jwks_cache

    if _jwks_cache is None:
        response = requests.get(JWKS_URL)
        if response.status_code != 200:
            raise Exception("Failed to fetch JWKS from Supabase")

        _jwks_cache = response.json()

    return _jwks_cache


def get_signing_key(token: str):
    jwks = get_jwks()

    headers = jwt.get_unverified_header(token)
    kid = headers.get("kid")

    for key in jwks.get("keys", []):
        if key.get("kid") == kid:
            return key

    raise Exception("Signing key not found for token (kid mismatch)")


def verify_jwt(token: str):
    try:
        key = get_signing_key(token)

        payload = jwt.decode(
            token,
            key,
            algorithms=ALGORITHMS,
            issuer=ISSUER,
            options={"verify_aud": False},  # Supabase uses 'authenticated'
        )

        return payload

    except Exception as e:
        print("JWT VERIFY ERROR:", str(e))
        raise HTTPException(status_code=401, detail="Invalid token")
