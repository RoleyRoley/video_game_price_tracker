from app.db.database import SessionLocal
from app.services.steam_service import SteamService
from app.services.game_service import save_game_and_price

# TESTING

db = SessionLocal()
steam = SteamService()

# Search for games and print results
try:
    #
    results = steam.search_games("cuphead", limit=5)
    if not results:
        print("No games found.")
    else:
        # For testing, we will take the first result and fetch its details, then save it to the database.
        selected_game = results[0]
        app_id = selected_game["appid"]

        # Fetch game details using the SteamService
        game_details = steam.get_game_details(app_id)

        if not game_details:
            print("Could not fetch game details.")
        else:
            # Save the game and its price history to the database
            game, price_record = save_game_and_price(db, game_details)

            print("Game saved successfully!")
            print(f"Game ID: {game.id}")
            print(f"Name: {game.name}")
            print(f"Steam App ID: {game.steam_app_id}")

            print("\nPrice history saved successfully!")
            print(f"Initial price: {price_record.initial_price}")
            print(f"Final price: {price_record.final_price}")
            print(f"Discount: {price_record.discount_percent}%")
            print(f"Currency: {price_record.currency}")

finally:
    db.close()