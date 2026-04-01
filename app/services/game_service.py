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


def save_game_and_price(db: session, game_details: dict):
    # Create the game if it does not exist yet, then insert a price snapshot.
    game = get_game_by_steam_app_id(db, game_details["steam_app_id"])
    if not game:
        game = create_game(
            db,
            steam_app_id=game_details["steam_app_id"],
            name=game_details.get("name", "Unknown"),
            steam_url=game_details.get("steam_url", "")
        )

    price_record = PriceHistory(
        game_id=game.id,
        initial_price=game_details.get("initial_price", 0),
        final_price=game_details.get("final_price", 0),
        discount_percent=game_details.get("discount_percent", 0),
        currency=game_details.get("currency", "GBP")
    )

    db.add(price_record)
    db.commit()
    db.refresh(price_record)
    return game, price_record