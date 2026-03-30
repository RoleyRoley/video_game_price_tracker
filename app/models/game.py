from sqlalchemy import Column, Integer, String
from app.db.database import Base

# Define the Game model
# This model represents a game in the database with its Steam app ID, name, and URL.

class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    steam_app_id = Column(Integer, unique=True, nullable=False)
    name = Column(String, nullable=False)
    steam_url = Column(String)