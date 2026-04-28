from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.auth.supabase_jwt import verify_supabase_jwt

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
):
    token = credentials.credentials

    return verify_supabase_jwt(token)
