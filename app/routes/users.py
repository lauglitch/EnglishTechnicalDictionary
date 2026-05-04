from fastapi import APIRouter, Depends, HTTPException
from app.auth.dependencies import get_current_user
from app.auth.permissions import verify_admin

router = APIRouter(prefix="/users", tags=["users"])


# -------------------------
# TEST ADMIN ROUTE
# -------------------------
@router.get("/admin")
def admin_route(user=Depends(get_current_user)):
    verify_admin(user)

    return {
        "message": "Admin access granted",
        "email": user.get("email"),
        "role": user.get("app_metadata", {}).get("role"),
    }


# -------------------------
# DEBUG ROUTE
# -------------------------
@router.get("/debug")
def debug_user(user=Depends(get_current_user)):
    return {
        "email": user.get("email"),
        "role": user.get("app_metadata", {}).get("role"),
        "raw": user,
    }
