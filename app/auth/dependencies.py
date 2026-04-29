from fastapi import Depends, HTTPException, Header
from jose import jwt
import requests
import os

SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_ISSUER = f"{SUPABASE_PROJECT_URL}/auth/v1"

JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/.well-known/jwks.json"


def get_jwks():
    response = requests.get(JWKS_URL)

    if response.status_code != 200:
        raise Exception("Failed to fetch JWKS")

    return response.json()


def get_current_user(authorization: str = Header(...)):
    try:
        token = authorization.split(" ")[1]

        jwks = get_jwks()

        headers = jwt.get_unverified_header(token)
        kid = headers["kid"]

        key = next(k for k in jwks["keys"] if k["kid"] == kid)

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
