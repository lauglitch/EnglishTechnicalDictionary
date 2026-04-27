import jwt
import requests
from fastapi import Header, HTTPException, Depends

SUPABASE_PROJECT_URL = "https://YOUR_PROJECT.supabase.co"
JWKS_URL = f"{SUPABASE_PROJECT_URL}/auth/v1/keys"

# cache keys (important for performance)
_jwks = requests.get(JWKS_URL).json()


def get_public_key(token):
    headers = jwt.get_unverified_header(token)
    kid = headers["kid"]

    for key in _jwks["keys"]:
        if key["kid"] == kid:
            return jwt.algorithms.RSAAlgorithm.from_jwk(key)

    raise HTTPException(401, "Invalid token key")


def verify_jwt(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(401, "Missing token")

    token = authorization.replace("Bearer ", "")

    try:
        public_key = get_public_key(token)

        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            audience="authenticated",
            issuer=f"{SUPABASE_PROJECT_URL}/auth/v1",
        )

        return payload

    except Exception as e:
        raise HTTPException(401, f"Invalid token: {str(e)}")


def require_admin(user=Depends(verify_jwt)):
    role = user.get("user_metadata", {}).get("role")

    if role != "admin":
        raise HTTPException(403, "Admin only")

    return user
