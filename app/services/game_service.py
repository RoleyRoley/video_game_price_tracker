from sqlalchemy.orm import session
from app.models.game import Game
from app.models.price_history import PriceHistory


def get_game_by_steam_app_id(db: session, steam_app_id: int):
    # Retrieve a game from the database using its Steam app ID.
    return db.query(Game).filter(Game.steam_app_id == steam_app_id).first() 

def create_game(db: session, steam_app_id: int, name: str, steam_url: str):
    
    # Create a new game entry in the database.
    game = Game(steam_app_id=steam_app_id, name=name, steam_url=steam_url)
    
    # Add the new game to the database and commit.
    db.add(game)
    db.commit() 
    db.refresh(game)
    return game