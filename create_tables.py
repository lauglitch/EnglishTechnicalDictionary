# CREATE SCHEMA
from backend.app.database import engine
from backend.app.models import Base


def create_tables():
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully")


if __name__ == "__main__":
    create_tables()
