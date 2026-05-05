from fastapi import HTTPException


def verify_admin(user: dict):
    """
    Validates Supabase admin role from JWT.
    """

    if not user:
        raise HTTPException(status_code=401, detail="Unauthenticated")

    role = user.get("app_metadata", {}).get("role")

    if role != "admin":
        raise HTTPException(status_code=403, detail="Not admin")


def is_admin(user: dict) -> bool:
    return user.get("app_metadata", {}).get("role") == "admin"
