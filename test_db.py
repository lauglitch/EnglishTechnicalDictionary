import os
from backend.app.database import engine
from sqlalchemy import text
from dotenv import load_dotenv

load_dotenv()

from backend.app.database import engine
from sqlalchemy import text


def test_connection():
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connected:", result.scalar())
    except Exception as e:
        print("❌ Connection failed:")
        print(e)


if __name__ == "__main__":
    test_connection()
