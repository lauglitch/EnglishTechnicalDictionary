from fastapi import HTTPException


def verify_admin(user: dict):
    """
    Checks if user has admin role in Supabase JWT (app_metadata).
    """

    if not user:
        raise HTTPException(status_code=401, detail="Unauthenticated")

    role = user.get("app_metadata", {}).get("role")

    if role != "admin":
        raise HTTPException(status_code=403, detail="Not admin")


def is_admin(user: dict) -> bool:
    """
    Optional helper if you want boolean checks.
    """
    return user.get("app_metadata", {}).get("role") == "admin"
