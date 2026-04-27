import os

ENVIRONMENT = os.getenv("ENVIRONMENT", "production")

IS_PRODUCTION = ENVIRONMENT == "production"
IS_STAGING = ENVIRONMENT == "staging"

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "").strip().lower()
DATABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_PROJECT_URL = os.getenv("SUPABASE_PROJECT_URL")
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")
