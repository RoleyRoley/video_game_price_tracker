# TEMP 

from app.db.database import engine, Base

# Import ALL models so SQLAlchemy knows about them
from app.models.game import Game

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Database tables created!")