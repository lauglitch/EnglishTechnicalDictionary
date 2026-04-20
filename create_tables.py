from app.database import engine
from app.models import Base, Word, Category, Example, UserProgress


def create_tables():
    print("Dropping and recreating database tables...")

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    print("✅ Tables recreated successfully")


if __name__ == "__main__":
    create_tables()
